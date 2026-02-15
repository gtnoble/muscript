"""
Semantic Analysis for Muslang
Validates AST, resolves references, expands constructs, and calculates timing.
"""

from muslang.ast_nodes import *
from muslang.config import *
from muslang import theory
from typing import List, Dict, Optional, Any
from dataclasses import replace


class SemanticError(Exception):
    """Exception raised for semantic errors"""
    pass


class SemanticAnalyzer:
    """Semantic analysis and AST transformation"""
    
    def __init__(self):
        self.symbol_table: Dict[str, List[ASTNode]] = {}
        self.current_time_sig = TimeSignature(numerator=4, denominator=4)
        self.current_key_sig: Optional[KeySignature] = None
        self.current_tempo = DEFAULT_TEMPO
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def analyze(self, ast: Sequence) -> Sequence:
        """Main entry point for semantic analysis"""
        # Phase 1: Validate structure
        self._validate_ast(ast)
        
        # Phase 2: Resolve variables
        ast = self._resolve_variables(ast)
        
        # Phase 3: Expand repeats
        ast = self._expand_repeats(ast)
        
        # Phase 4: Apply key signatures
        ast = self._apply_key_signatures(ast)
        
        # Phase 5: Expand ornaments
        ast = self._expand_ornaments(ast)
        
        # Phase 6: Calculate timing
        ast = self._calculate_timing(ast)
        
        # Phase 7: Track state
        ast = self._track_state(ast)
        
        if self.errors:
            raise SemanticError("\n".join(self.errors))
        
        return ast
    
    def _validate_ast(self, node: ASTNode):
        """Validate AST structure"""
        if isinstance(node, Note):
            # Validate pitch range
            if node.octave < 0 or node.octave > 10:
                self._error(f"Octave out of range: {node.octave}")
            
            # Validate duration
            if node.duration and node.duration not in [1, 2, 4, 8, 16, 32, 64]:
                self._error(f"Invalid duration: {node.duration}")
        
        elif isinstance(node, Slur):
            if len(node.notes) < 2:
                self._error("Slur must contain at least 2 notes")
        
        elif isinstance(node, Slide):
            # Check pitch interval
            from_midi = self._note_to_midi(node.from_note)
            to_midi = self._note_to_midi(node.to_note)
            if abs(from_midi - to_midi) > 24:
                self._warning(f"Large slide interval: {abs(from_midi - to_midi)} semitones")
        
        elif isinstance(node, Tuplet):
            if node.ratio < 2:
                self._error("Tuplet ratio must be >= 2")
        
        elif isinstance(node, TimeSignature):
            if node.numerator < 1:
                self._error(f"Time signature numerator must be >= 1: {node.numerator}")
            if node.denominator not in [1, 2, 4, 8, 16, 32]:
                self._error(f"Invalid time signature denominator: {node.denominator}")
        
        elif isinstance(node, Tempo):
            if node.bpm < 20 or node.bpm > 400:
                self._warning(f"Unusual tempo: {node.bpm} BPM")
        
        # Recursively validate children
        for child in self._get_children(node):
            self._validate_ast(child)
    
    def _resolve_variables(self, node: ASTNode) -> ASTNode:
        """Resolve variable references"""
        if isinstance(node, Variable):
            self.symbol_table[node.name] = node.value
            return None  # Remove variable definitions from event stream
        
        elif isinstance(node, VariableReference):
            if node.name not in self.symbol_table:
                self._error(f"Undefined variable: ${node.name}")
                return node
            # Replace reference with expanded value
            return Sequence(events=self.symbol_table[node.name])
        
        # Recursively process
        return self._transform_children(node, self._resolve_variables)
    
    def _expand_repeats(self, node: ASTNode) -> ASTNode:
        """Expand repeat constructs"""
        if isinstance(node, Repeat):
            expanded = []
            for _ in range(node.count):
                # Recursively expand each element in case there are nested repeats
                for item in node.sequence:
                    expanded_item = self._expand_repeats(item)
                    expanded.append(expanded_item)
            return Sequence(events=expanded)
        
        elif isinstance(node, (Sequence, Instrument)):
            # Recursively process children
            return self._transform_children(node, self._expand_repeats)
        
        return node
    
    def _apply_key_signatures(self, node: ASTNode) -> ASTNode:
        """Apply key signature accidentals to notes"""
        if isinstance(node, KeySignature):
            # Create KeySignatureInfo object for tracking
            # Construct root with accidental if present (e.g., 'a-', 'f+')
            root = node.root
            if node.accidental == 'sharp':
                root += '+'
            elif node.accidental == 'flat':
                root += '-'
            key_info = theory.KeySignatureInfo(root, node.mode)
            self.current_key_sig = key_info
            return node
        
        elif isinstance(node, Note):
            if self.current_key_sig and node.accidental is None:
                # Apply key signature using theory module
                return theory.apply_key_signature_to_note(node, self.current_key_sig)
        
        return self._transform_children(node, self._apply_key_signatures)
    
    def _expand_ornaments(self, node: ASTNode) -> ASTNode:
        """Expand ornaments into note sequences"""
        if isinstance(node, Instrument):
            # Process non-voice events
            expanded = []
            i = 0
            while i < len(node.events):
                event = node.events[i]
                
                if isinstance(event, Ornament) and i + 1 < len(node.events):
                    next_event = node.events[i + 1]
                    if isinstance(next_event, Note):
                        # Expand ornament
                        notes = self._expand_single_ornament(event, next_event)
                        expanded.extend(notes)
                        i += 2  # Skip both ornament and note
                        continue
                
                # Recursively process event
                processed = self._expand_ornaments(event)
                expanded.append(processed)
                i += 1
            
            # Process voice events
            expanded_voices = {}
            for voice_num, voice_events in node.voices.items():
                expanded_voice = []
                i = 0
                while i < len(voice_events):
                    event = voice_events[i]
                    
                    if isinstance(event, Ornament) and i + 1 < len(voice_events):
                        next_event = voice_events[i + 1]
                        if isinstance(next_event, Note):
                            # Expand ornament
                            notes = self._expand_single_ornament(event, next_event)
                            expanded_voice.extend(notes)
                            i += 2  # Skip both ornament and note
                            continue
                    
                    # Recursively process event
                    processed = self._expand_ornaments(event)
                    expanded_voice.append(processed)
                    i += 1
                
                expanded_voices[voice_num] = expanded_voice
            
            return replace(node, events=expanded, voices=expanded_voices)
        
        elif isinstance(node, Sequence):
            if node.instruments:
                # Top-level sequence - process instruments
                expanded_instruments = {}
                for name, inst in node.instruments.items():
                    expanded_instruments[name] = self._expand_ornaments(inst)
                return replace(node, instruments=expanded_instruments)
            else:
                # Sub-sequence - process events list
                expanded = []
                i = 0
                while i < len(node.events):
                    event = node.events[i]
                    
                    if isinstance(event, Ornament) and i + 1 < len(node.events):
                        next_event = node.events[i + 1]
                        if isinstance(next_event, Note):
                            # Expand ornament
                            notes = self._expand_single_ornament(event, next_event)
                            expanded.extend(notes)
                            i += 2  # Skip both ornament and note
                            continue
                    
                    # Recursively process event
                    processed = self._expand_ornaments(event)
                    expanded.append(processed)
                    i += 1
                
                return replace(node, events=expanded)
        
        return node
    
    def _expand_single_ornament(self, ornament: Ornament, note: Note) -> List[Note]:
        """Expand a single ornament into notes using theory module"""
        # Use theory module to expand ornament
        return theory.expand_ornament(ornament.type, note, self.current_key_sig)
    
    def _calculate_timing(self, node: ASTNode) -> ASTNode:
        """Calculate absolute timing for all events"""
        if isinstance(node, Instrument):
            # Handle voices - each voice starts at time 0 independently
            if node.voices:
                updated_voices = {}
                for voice_num, voice_events in node.voices.items():
                    current_time = 0.0
                    updated_events = []
                    for event in voice_events:
                        event_with_timing, duration = self._calculate_event_timing(event, current_time)
                        updated_events.append(event_with_timing)
                        current_time += duration
                    updated_voices[voice_num] = updated_events
                
                # Also handle non-voice events (sequential from time 0)
                current_time = 0.0
                updated_events = []
                for event in node.events:
                    event_with_timing, duration = self._calculate_event_timing(event, current_time)
                    updated_events.append(event_with_timing)
                    current_time += duration
                
                return replace(node, events=updated_events, voices=updated_voices)
            else:
                # No voices - calculate timing for events sequentially
                current_time = 0.0
                updated_events = []
                for event in node.events:
                    event_with_timing, duration = self._calculate_event_timing(event, current_time)
                    updated_events.append(event_with_timing)
                    current_time += duration
                return replace(node, events=updated_events)
        
        elif isinstance(node, Sequence):
            # Handle instruments dict or events list
            if node.instruments:
                # Top-level sequence - process each instrument
                updated_instruments = {}
                for name, inst in node.instruments.items():
                    updated_instruments[name] = self._calculate_timing(inst)
                return replace(node, instruments=updated_instruments)
            else:
                # Sub-sequence - process events
                updated_events = []
                for event in node.events:
                    updated_events.append(self._calculate_timing(event))
                return replace(node, events=updated_events)
        
        return node
    
    def _calculate_event_timing(self, event: ASTNode, start_time: float) -> tuple[ASTNode, float]:
        """
        Calculate timing for a single event.
        Returns (updated_event, duration_in_ticks)
        """
        if isinstance(event, Note):
            duration_ticks = self._duration_to_ticks(event.duration or DEFAULT_NOTE_DURATION, event.dotted)
            end_time = start_time + duration_ticks
            updated_note = replace(event, start_time=start_time, end_time=end_time)
            return updated_note, duration_ticks
        
        elif isinstance(event, Rest):
            duration_ticks = self._duration_to_ticks(event.duration or DEFAULT_NOTE_DURATION, event.dotted)
            end_time = start_time + duration_ticks
            updated_rest = replace(event, start_time=start_time, end_time=end_time)
            return updated_rest, duration_ticks
        
        elif isinstance(event, Chord):
            # All notes in chord have same timing
            max_duration = 0.0
            updated_notes = []
            
            for note in event.notes:
                duration_ticks = self._duration_to_ticks(note.duration or DEFAULT_NOTE_DURATION, note.dotted)
                end_time = start_time + duration_ticks
                updated_note = replace(note, start_time=start_time, end_time=end_time)
                updated_notes.append(updated_note)
                max_duration = max(max_duration, duration_ticks)
            
            updated_chord = replace(event, notes=updated_notes, start_time=start_time, end_time=start_time + max_duration)
            return updated_chord, max_duration
        
        elif isinstance(event, PercussionNote):
            duration_ticks = self._duration_to_ticks(event.duration or DEFAULT_NOTE_DURATION, event.dotted)
            end_time = start_time + duration_ticks
            updated_perc = replace(event, start_time=start_time, end_time=end_time)
            return updated_perc, duration_ticks
        
        elif isinstance(event, Tuplet):
            # Tuplets scale time: ratio notes fit into actual_duration space
            # For example, triplet (ratio=3) fits 3 notes in space of 2
            actual_ticks = self._duration_to_ticks(event.actual_duration, False)
            time_per_note = actual_ticks / event.ratio
            
            current_tuplet_time = start_time
            updated_notes = []
            
            for note in event.notes:
                # Each note in tuplet gets scaled duration
                end_time = current_tuplet_time + time_per_note
                updated_note = replace(note, start_time=current_tuplet_time, end_time=end_time)
                updated_notes.append(updated_note)
                current_tuplet_time += time_per_note
            
            return replace(event, notes=updated_notes), actual_ticks
        
        elif isinstance(event, GraceNote):
            # Grace note steals time from beginning (small fixed duration)
            grace_duration = DEFAULT_MIDI_PPQ * GRACE_NOTE_DURATION_RATIO
            end_time = start_time + grace_duration
            updated_grace_note = replace(event.note, start_time=start_time, end_time=end_time)
            return replace(event, note=updated_grace_note), grace_duration
        
        elif isinstance(event, Slur):
            # Process notes in slur, they advance time sequentially
            current_slur_time = start_time
            updated_notes = []
            
            for note in event.notes:
                updated_note, duration = self._calculate_event_timing(note, current_slur_time)
                updated_notes.append(updated_note)
                current_slur_time += duration
            
            total_duration = current_slur_time - start_time
            return replace(event, notes=updated_notes), total_duration
        
        elif isinstance(event, Slide):
            # Slide takes the duration of the from_note
            from_note_updated, duration = self._calculate_event_timing(event.from_note, start_time)
            # to_note happens at the end (same endpoint)
            to_note_updated = replace(event.to_note, start_time=start_time, end_time=start_time + duration)
            return replace(event, from_note=from_note_updated, to_note=to_note_updated), duration
        
        elif isinstance(event, Tempo):
            # Tempo changes affect subsequent timing but don't consume time themselves
            self.current_tempo = event.bpm
            return event, 0.0
        
        elif isinstance(event, TimeSignature):
            # Time signature changes affect beat calculation but don't consume time
            self.current_time_sig = event
            return event, 0.0
        
        elif isinstance(event, (KeySignature, Pan, Articulation, DynamicLevel, DynamicTransition, DynamicAccent, Reset, Ornament, Expression)):
            # These directives don't consume time
            return event, 0.0
        
        else:
            # Unknown event type, doesn't consume time
            return event, 0.0
    
    def _duration_to_ticks(self, duration: int, dotted: bool) -> float:
        """
        Convert note duration to MIDI ticks.
        
        Args:
            duration: Note duration (1=whole, 2=half, 4=quarter, etc.)
            dotted: Whether the note is dotted (1.5x duration)
        
        Returns:
            Duration in MIDI ticks (float)
        """
        # duration: 1=whole, 2=half, 4=quarter, etc.
        # A whole note = 4 quarter notes = 4 * PPQ ticks
        ticks = (4 * DEFAULT_MIDI_PPQ) / duration
        
        if dotted:
            ticks *= DOT_MULTIPLIER
        
        return ticks
    
    def _track_state(self, node: ASTNode) -> ASTNode:
        """Track articulation and dynamic state"""
        if isinstance(node, Instrument):
            # Track state through the instrument's events
            state = {
                'articulation': 'natural',
                'dynamic_level': 'mf',
                'velocity': VELOCITY_MF,
                'transition_active': None,  # 'crescendo' or 'diminuendo'
                'transition_start_velocity': None,
                'transition_target_velocity': None,
            }
            
            # Process non-voice events
            updated_events = []
            for event in node.events:
                updated_event = self._apply_state_to_event(event, state)
                updated_events.append(updated_event)
            
            # Process voice events - each voice has independent state
            updated_voices = {}
            for voice_num, voice_events in node.voices.items():
                # Reset state for each voice
                voice_state = {
                    'articulation': 'natural',
                    'dynamic_level': 'mf',
                    'velocity': VELOCITY_MF,
                    'transition_active': None,
                    'transition_start_velocity': None,
                    'transition_target_velocity': None,
                }
                updated_voice_events = []
                for event in voice_events:
                    updated_event = self._apply_state_to_event(event, voice_state)
                    updated_voice_events.append(updated_event)
                updated_voices[voice_num] = updated_voice_events
            
            return replace(node, events=updated_events, voices=updated_voices)
        
        elif isinstance(node, Sequence):
            # Handle instruments dict or events list
            if node.instruments:
                # Top-level sequence - process each instrument
                updated_instruments = {}
                for name, inst in node.instruments.items():
                    updated_instruments[name] = self._track_state(inst)
                return replace(node, instruments=updated_instruments)
            else:
                # Sub-sequence - process events
                updated_events = []
                for event in node.events:
                    updated_events.append(self._track_state(event))
                return replace(node, events=updated_events)
        
        return node
    
    def _apply_state_to_event(self, event: ASTNode, state: dict) -> ASTNode:
        """
        Apply current articulation and dynamic state to an event.
        Updates state dict in place for subsequent events.
        """
        if isinstance(event, Articulation):
            # Update articulation state
            state['articulation'] = event.type
            return event
        
        elif isinstance(event, Reset):
            # Reset articulation to natural
            if event.type in ('natural', 'full'):
                state['articulation'] = 'natural'
            if event.type == 'full':
                state['dynamic_level'] = 'mf'
                state['velocity'] = VELOCITY_MF
                state['transition_active'] = None
            return event
        
        elif isinstance(event, DynamicLevel):
            # Set new dynamic level
            state['dynamic_level'] = event.level
            state['velocity'] = self._dynamic_level_to_velocity(event.level)
            state['transition_active'] = None  # Clear any active transition
            return event
        
        elif isinstance(event, DynamicTransition):
            # Start crescendo or diminuendo
            state['transition_active'] = event.type
            state['transition_start_velocity'] = state['velocity']
            # Target depends on direction
            if event.type == 'crescendo':
                state['transition_target_velocity'] = min(127, state['velocity'] + 40)
            else:  # diminuendo
                state['transition_target_velocity'] = max(0, state['velocity'] - 40)
            return event
        
        elif isinstance(event, DynamicAccent):
            # One-shot accent - doesn't change state
            return event
        
        elif isinstance(event, Note):
            # Apply current state to note
            velocity = self._calculate_note_velocity(state, event)
            return replace(event, 
                         velocity=velocity,
                         articulation=state['articulation'],
                         dynamic_level=state['dynamic_level'])
        
        elif isinstance(event, Chord):
            # Apply state to all notes in chord
            updated_notes = []
            for note in event.notes:
                velocity = self._calculate_note_velocity(state, note)
                updated_note = replace(note,
                                     velocity=velocity,
                                     articulation=state['articulation'],
                                     dynamic_level=state['dynamic_level'])
                updated_notes.append(updated_note)
            return replace(event, notes=updated_notes)
        
        elif isinstance(event, PercussionNote):
            # Apply velocity to percussion
            velocity = self._calculate_note_velocity(state, event)
            return replace(event, velocity=velocity)
        
        elif isinstance(event, Tuplet):
            # Apply state to notes in tuplet
            updated_notes = []
            for note in event.notes:
                velocity = self._calculate_note_velocity(state, note)
                updated_note = replace(note,
                                     velocity=velocity,
                                     articulation=state['articulation'],
                                     dynamic_level=state['dynamic_level'])
                updated_notes.append(updated_note)
            return replace(event, notes=updated_notes)
        
        elif isinstance(event, GraceNote):
            # Apply state to grace note
            velocity = self._calculate_note_velocity(state, event.note)
            updated_note = replace(event.note,
                                 velocity=velocity,
                                 articulation=state['articulation'],
                                 dynamic_level=state['dynamic_level'])
            return replace(event, note=updated_note)
        
        elif isinstance(event, Slur):
            # Apply state to notes in slur
            updated_notes = []
            for note in event.notes:
                updated_note = self._apply_state_to_event(note, state)
                updated_notes.append(updated_note)
            return replace(event, notes=updated_notes)
        
        elif isinstance(event, Slide):
            # Apply state to both notes in slide
            from_note_updated = self._apply_state_to_event(event.from_note, state)
            to_note_updated = self._apply_state_to_event(event.to_note, state)
            return replace(event, from_note=from_note_updated, to_note=to_note_updated)
        
        else:
            # Other event types don't need state tracking
            return event
    
    def _dynamic_level_to_velocity(self, level: str) -> int:
        """Convert dynamic level to MIDI velocity"""
        velocity_map = {
            'pp': VELOCITY_PP,
            'p': VELOCITY_P,
            'mp': VELOCITY_MP,
            'mf': VELOCITY_MF,
            'f': VELOCITY_F,
            'ff': VELOCITY_FF,
        }
        return velocity_map.get(level, VELOCITY_MF)
    
    def _calculate_note_velocity(self, state: dict, note: ASTNode) -> int:
        """
        Calculate MIDI velocity for a note based on current dynamic state.
        Handles crescendo/diminuendo transitions.
        """
        velocity = state['velocity']
        
        # Handle crescendo/diminuendo
        if state['transition_active']:
            # Gradually move towards target
            target = state['transition_target_velocity']
            if state['transition_active'] == 'crescendo':
                velocity = min(target, velocity + DYNAMIC_TRANSITION_STEP)
            else:  # diminuendo
                velocity = max(target, velocity - DYNAMIC_TRANSITION_STEP)
            
            # Update state velocity for next note
            state['velocity'] = velocity
        
        # Clamp to valid MIDI range
        return max(0, min(127, velocity))
    
    def _get_children(self, node: ASTNode) -> List[ASTNode]:
        """Get child nodes for traversal"""
        if isinstance(node, Sequence):
            # For top-level sequences, return instruments; for sub-sequences, return events
            if node.instruments:
                return list(node.instruments.values())
            else:
                return node.events
        elif isinstance(node, Instrument):
            # Collect both non-voice events and all voice events
            children = list(node.events)
            for voice_events in node.voices.values():
                children.extend(voice_events)
            return children
        elif isinstance(node, Slur):
            return node.notes
        elif isinstance(node, Chord):
            return node.notes
        elif isinstance(node, Tuplet):
            return node.notes
        elif isinstance(node, Repeat):
            return node.sequence
        elif isinstance(node, Variable):
            return node.value
        else:
            return []
    
    def _transform_children(self, node: ASTNode, transform_func) -> ASTNode:
        """Apply transformation to children and return new node"""
        if isinstance(node, Sequence):
            if node.instruments:
                # Top-level sequence with instruments dict
                new_instruments = {}
                for name, inst in node.instruments.items():
                    result = transform_func(inst)
                    if result is not None:
                        new_instruments[name] = result
                return replace(node, instruments=new_instruments)
            else:
                # Sub-sequence with events list
                new_events = []
                for event in node.events:
                    result = transform_func(event)
                    if result is not None:
                        if isinstance(result, Sequence):
                            # Flatten sequences
                            new_events.extend(result.events)
                        else:
                            new_events.append(result)
                return replace(node, events=new_events)
        
        elif isinstance(node, Instrument):
            # Transform non-voice events
            new_events = []
            for event in node.events:
                result = transform_func(event)
                if result is not None:
                    if isinstance(result, Sequence):
                        new_events.extend(result.events)
                    else:
                        new_events.append(result)
            
            # Transform voice events
            new_voices = {}
            for voice_num, voice_events in node.voices.items():
                new_voice_events = []
                for event in voice_events:
                    result = transform_func(event)
                    if result is not None:
                        if isinstance(result, Sequence):
                            new_voice_events.extend(result.events)
                        else:
                            new_voice_events.append(event)
                new_voices[voice_num] = new_voice_events
            
            return replace(node, events=new_events, voices=new_voices)
        
        elif isinstance(node, Slur):
            new_notes = [transform_func(n) for n in node.notes if transform_func(n) is not None]
            return replace(node, notes=new_notes)
        
        elif isinstance(node, Chord):
            new_notes = [transform_func(n) for n in node.notes if transform_func(n) is not None]
            return replace(node, notes=new_notes)
        
        elif isinstance(node, Tuplet):
            new_notes = [transform_func(n) for n in node.notes if transform_func(n) is not None]
            return replace(node, notes=new_notes)
        
        else:
            return node
    
    def _note_to_midi(self, note: Note) -> int:
        """Convert note to MIDI note number"""
        pitch_map = {'c': 0, 'd': 2, 'e': 4, 'f': 5, 'g': 7, 'a': 9, 'b': 11}
        midi_note = (note.octave + 1) * 12 + pitch_map[note.pitch]
        
        if note.accidental == 'sharp':
            midi_note += 1
        elif note.accidental == 'flat':
            midi_note -= 1
        
        return midi_note
    
    def _error(self, message: str):
        """Record an error"""
        self.errors.append(message)
    
    def _warning(self, message: str):
        """Record a warning"""
        self.warnings.append(message)
