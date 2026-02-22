"""
Parser for Muslang music DSL.

This module implements the parser that converts Lark parse trees into Muslang AST nodes.
It uses a Lark Transformer to traverse the parse tree and build the Abstract Syntax Tree.

The parser uses scientific pitch notation with NO stateful octave tracking:
- Notes are specified as pitch+octave: c4/4 (C octave 4, quarter note)
- Octave is always explicit in the notation
- current_duration: Default duration for notes without explicit duration (default: 1)

Key features:
- Scientific pitch notation (c4, d5, etc.) - octave always specified
- Default duration inheritance
- Voice context tracking for polyphonic instruments
- Source location preservation for error reporting
- Graceful handling of optional elements (accidentals, durations, dots)
- Operator prefixes: : (articulation), @ (dynamics), % (ornaments)
"""

from pathlib import Path
from typing import Optional, List, Any
from lark import Lark, Transformer, Token, Tree, v_args
from lark.exceptions import LarkError

from .ast_nodes import (
    Note, Rest, PercussionNote,
    GraceNote, Tuplet,
    Slide, Measure,
    Articulation, Ornament, Tremolo, Reset, Expression,
    DynamicLevel, DynamicTransition, DynamicAccent,
    TimeSignature, KeySignature, Tempo, Pan,
    Voice, Instrument, Sequence,
    SourceLocation,
)
from .config import DEFAULT_NOTE_DURATION


class MuslangTransformer(Transformer):
    """
    Lark Transformer that converts parse trees into Muslang AST nodes.
    
    This transformer maintains minimal parser state and converts each grammar rule
    into the appropriate AST node. Uses scientific pitch notation with NO stateful
    octave tracking.
    
    State variables:
        current_duration: Current default duration (default: 1 for whole note)
        current_voice: Current voice number (None for main voice)
    """
    
    def __init__(self):
        """Initialize the transformer with default state."""
        super().__init__()
        self.current_duration = DEFAULT_NOTE_DURATION
        self.current_voice: Optional[int] = None
    
    def _get_location(self, meta) -> Optional[SourceLocation]:
        """
        Extract source location from Lark meta object.
        
        Args:
            meta: Lark meta object containing line and column information
            
        Returns:
            SourceLocation object or None if meta not available
        """
        if hasattr(meta, 'line') and hasattr(meta, 'column'):
            return SourceLocation(line=meta.line, column=meta.column)
        return None
    
    # ========================================================================
    # Top-Level Structure
    # ========================================================================
    
    def composition_event(self, items):
        """
        Transform composition-level event (directive, articulation, or dynamic).
        
        Grammar: composition_event: (directive | articulation | dynamic_level | dynamic_transition) ";"
        
        Args:
            items: [directive/articulation/dynamic node] (semicolon consumed by grammar)
            
        Returns:
            The event node with scope='composition'
        """
        event = items[0]
        # Tag with composition scope
        if hasattr(event, 'scope'):
            event.scope = 'composition'
        return event

    def composition_item(self, items):
        """Unwrap composition_item to its contained event or instrument."""
        return items[0]
    
    def composition(self, items) -> Sequence:
        """
        Transform composition into Sequence with instruments dict and composition defaults.
        
        Multiple declarations of the same instrument are merged by
        concatenating their events in order of appearance.
        
        Args:
            items: List of composition_events and Instrument nodes
            
        Returns:
            Sequence node with instruments dict and composition_defaults
        """
        composition_defaults = {}
        instruments = {}
        composition_scope = {
            'tempo': None,
            'time_signature': None,
            'key_signature': None,
            'pan': None,
            'articulation': None,
            'dynamic_level': None,
            'dynamic_transition': None,
        }
        first_instrument_seen = False

        def _scope_events() -> List[Any]:
            """Return active composition-scope events in deterministic order."""
            ordered_keys = [
                'tempo',
                'time_signature',
                'key_signature',
                'pan',
                'articulation',
                'dynamic_level',
                'dynamic_transition',
            ]
            return [composition_scope[key] for key in ordered_keys if composition_scope[key] is not None]
        
        for item in items:
            # Check if this is a composition-level event
            if hasattr(item, 'scope') and item.scope == 'composition':
                # Update active composition scope
                if isinstance(item, Tempo):
                    composition_scope['tempo'] = item
                elif isinstance(item, TimeSignature):
                    composition_scope['time_signature'] = item
                elif isinstance(item, KeySignature):
                    composition_scope['key_signature'] = item
                elif isinstance(item, Pan):
                    composition_scope['pan'] = item
                elif isinstance(item, Articulation):
                    composition_scope['articulation'] = item
                elif isinstance(item, DynamicLevel):
                    composition_scope['dynamic_level'] = item
                elif isinstance(item, DynamicTransition):
                    composition_scope['dynamic_transition'] = item
                continue
            
            # This is an instrument
            inst = item

            # Capture composition defaults from scope at first instrument only
            if not first_instrument_seen:
                if composition_scope['tempo'] is not None:
                    composition_defaults['tempo'] = composition_scope['tempo'].bpm
                if composition_scope['time_signature'] is not None:
                    composition_defaults['time_signature'] = composition_scope['time_signature']
                if composition_scope['key_signature'] is not None:
                    composition_defaults['key_signature'] = composition_scope['key_signature']
                if composition_scope['pan'] is not None:
                    composition_defaults['pan'] = composition_scope['pan'].position
                if composition_scope['articulation'] is not None:
                    composition_defaults['articulation'] = composition_scope['articulation'].type
                if composition_scope['dynamic_level'] is not None:
                    composition_defaults['dynamic_level'] = composition_scope['dynamic_level'].level
                if composition_scope['dynamic_transition'] is not None:
                    composition_defaults['dynamic_transition'] = composition_scope['dynamic_transition']
                first_instrument_seen = True

            # Inject active composition-scope events into each voice so interleaved
            # top-level directives/dynamics/articulations affect subsequent blocks.
            active_scope_events = _scope_events()
            if active_scope_events and inst.voices:
                injected_voices = {}
                for voice_num, voice_events in inst.voices.items():
                    injected_voices[voice_num] = active_scope_events + voice_events
                inst = Instrument(
                    name=inst.name,
                    events=inst.events,
                    voices=injected_voices,
                    defaults_sequence=inst.defaults_sequence,
                )
            
            if inst.name in instruments:
                # Merge: concatenate events to existing instrument
                existing = instruments[inst.name]
                # Merge events
                merged_events = existing.events + inst.events
                # Merge voices
                merged_voices = dict(existing.voices)
                for voice_num, voice_events in inst.voices.items():
                    if voice_num in merged_voices:
                        merged_voices[voice_num] = merged_voices[voice_num] + voice_events
                    else:
                        merged_voices[voice_num] = voice_events
                # Merge defaults_sequence
                merged_defaults_seq = existing.defaults_sequence + inst.defaults_sequence
                instruments[inst.name] = Instrument(
                    name=inst.name,
                    events=merged_events,
                    voices=merged_voices,
                    defaults_sequence=merged_defaults_seq
                )
            else:
                instruments[inst.name] = inst
        
        return Sequence(
            instruments=instruments,
            events=[],  # No longer used for directives
            composition_defaults=composition_defaults
        )
    
    def instrument_event(self, items):
        """
        Transform instrument-level event (directive, articulation, or dynamic).
        
        Grammar: instrument_event: (directive | articulation | dynamic_level | dynamic_transition | dynamic_accent) ";"
        
        Args:
            items: [directive/articulation/dynamic node] (semicolon consumed by grammar)
            
        Returns:
            The event node with scope='instrument'
        """
        event = items[0]
        # Tag with instrument scope
        if hasattr(event, 'scope'):
            event.scope = 'instrument'
        return event
    
    def instrument_body(self, items) -> dict:
        """
        Transform instrument body containing instrument events and voice content.
        
        Grammar: instrument_body: (instrument_event | voice_content)+
        
        Instrument events apply sequentially to voices that follow them.
        
        Args:
            items: List of instrument_events and voice_content dicts (interleaved)
            
        Returns:
            Dict with 'voices', 'defaults_sequence' keys
        """
        # Process items sequentially - track current defaults
        voices = {}
        defaults_sequence = []
        current_defaults = {}
        current_scope_events = {
            'tempo': None,
            'time_signature': None,
            'key_signature': None,
            'pan': None,
            'articulation': None,
            'dynamic_level': None,
            'dynamic_transition': None,
            'dynamic_accent': None,
        }

        def _scope_events() -> List[Any]:
            ordered_keys = [
                'tempo',
                'time_signature',
                'key_signature',
                'pan',
                'articulation',
                'dynamic_level',
                'dynamic_transition',
                'dynamic_accent',
            ]
            return [current_scope_events[key] for key in ordered_keys if current_scope_events[key] is not None]
        
        for item in items:
            if hasattr(item, 'scope') and item.scope == 'instrument':
                # Update current defaults with this event
                if isinstance(item, Tempo):
                    current_defaults['tempo'] = item.bpm
                    current_scope_events['tempo'] = item
                elif isinstance(item, TimeSignature):
                    current_defaults['time_signature'] = item
                    current_scope_events['time_signature'] = item
                elif isinstance(item, KeySignature):
                    current_defaults['key_signature'] = item
                    current_scope_events['key_signature'] = item
                elif isinstance(item, Pan):
                    current_defaults['pan'] = item.position
                    current_scope_events['pan'] = item
                elif isinstance(item, Articulation):
                    current_defaults['articulation'] = item.type
                    current_scope_events['articulation'] = item
                elif isinstance(item, DynamicLevel):
                    current_defaults['dynamic_level'] = item.level
                    current_scope_events['dynamic_level'] = item
                elif isinstance(item, DynamicTransition):
                    current_defaults['dynamic_transition'] = item
                    current_scope_events['dynamic_transition'] = item
                elif isinstance(item, DynamicAccent):
                    current_defaults['dynamic_accent'] = item
                    current_scope_events['dynamic_accent'] = item
                    
            elif isinstance(item, dict):
                # Voice content - apply current defaults
                voice_num = list(item.keys())[0]
                voice_events = item[voice_num]
                segment_events = _scope_events() + voice_events
                
                # Associate this voice with current defaults
                defaults_sequence.append((voice_num, current_defaults.copy()))
                if voice_num in voices:
                    voices[voice_num] = voices[voice_num] + segment_events
                else:
                    voices[voice_num] = segment_events
        
        return {
            'voices': voices,
            'defaults_sequence': defaults_sequence
        }
    
    def instrument(self, items) -> Instrument:
        """
        Transform instrument declaration.
        
        Grammar: instrument: INSTRUMENT_NAME "{" instrument_body "}"
        
        Args:
            items: [Token(INSTRUMENT_NAME), instrument_body_dict]
            
        Returns:
            Instrument node with name, voices, and defaults_sequence populated
        """
        name_token = items[0]
        instrument_name = str(name_token)
        
        # Extract instrument_body dict
        body_dict = items[1] if len(items) > 1 else {'voices': {}, 'defaults_sequence': []}
        
        voices = body_dict.get('voices', {})
        defaults_sequence = body_dict.get('defaults_sequence', [])
        
        # Reset state for each instrument
        self.current_duration = DEFAULT_NOTE_DURATION
        self.current_voice = None
        
        # Require at least one voice
        if not voices:
            raise ValueError(
                f"Error in instrument '{instrument_name}': "
                f"At least one voice (e.g., V1:) is required with measures."
            )
        
        return Instrument(
            name=instrument_name,
            events=[],  # No longer used
            voices=voices,
            defaults_sequence=defaults_sequence
        )
    
    def voice_content(self, items) -> dict:
        """
        Transform voice content (VOICE ":" measures).
        
        Grammar: voice_content: VOICE ":" measures
        
        Args:
            items: [Token(VOICE), measures_list]
            
        Returns:
            Dict mapping voice number to measures list
        """
        voice_token = items[0]
        measures_list = items[1]
        
        # Extract number from VOICE token (e.g., "V1" -> 1)
        voice_number = int(str(voice_token)[1:])  # Skip the 'V' prefix
        
        return {voice_number: measures_list}
    
    def measures(self, items) -> List[Measure]:
        """
        Transform measures list (measure (\"|\", measure)* \"|\").
        
        Grammar: measures: measure ("|" measure)* "|"
        
        Args:
            items: List of Measure nodes (bar line tokens are consumed by grammar)
            
        Returns:
            List of Measure nodes with measure numbers assigned
        """
        measure_list = [item for item in items if isinstance(item, Measure)]
        
        # Assign measure numbers (1-indexed)
        for idx, measure in enumerate(measure_list, start=1):
            measure.measure_number = idx
        
        return measure_list
    
    @v_args(meta=True)
    def measure(self, items, meta) -> Measure:
        """
        Transform measure (measure_event+).
        
        Grammar: measure: measure_event+
        
        Args:
            items: List of event nodes
            meta: Lark meta object with source location information
            
        Returns:
            Measure node containing the events
        """
        location = self._get_location(meta)
        return Measure(events=items, location=location)
    
    # ========================================================================
    # Notes and Basic Rhythm
    # ========================================================================
    
    def note(self, items) -> Note:
        """
        Transform note with scientific pitch notation.
        
        Grammar: note: NOTE_NAME accidental? ("/" duration dotted?)?
        NOTE_NAME format: pitch+octave (e.g., c4, d5, a3)
        
        Args:
            items: [Token(NOTE_NAME), accidental?, duration?, dotted?]
            
        Returns:
            Note node
        """
        note_name_token = items[0]
        note_name = str(note_name_token).lower()
        
        # Debug: print what we received
        # print(f"DEBUG note transformer received: {items}")
        # print(f"  Types: {[type(i).__name__ for i in items]}")
        # for i, item in enumerate(items):
        #     if isinstance(item, Tree):
        #         print(f"    Tree {i}: data={item.data}, children={item.children}")
        
        # Parse NOTE_NAME: first char is pitch, second is octave digit
        pitch = note_name[0]  # e.g., 'c' from 'c4'
        octave = int(note_name[1])  # e.g., 4 from 'c4'
        
        # Extract optional elements
        accidental = None
        duration = None
        dotted = False
        
        for item in items[1:]:
            if isinstance(item, Tree):
                # Handle tree nodes from inline rules (duration, etc.)
                if item.data == 'duration' and item.children:
                    # Duration tree has the matched token as child
                    duration_token = item.children[0]
                    duration = int(str(duration_token))
                elif item.data == 'dotted':
                    dotted = True
                elif item.data == 'accidental' and item.children:
                    acc_token = str(item.children[0])
                    accidental = {'+': 'sharp', '-': 'flat'}[acc_token]
            elif isinstance(item, Token):
                item_str = str(item)
                # Check if it's a duration value
                if item_str in ['1', '2', '4', '8', '16', '32', '64']:
                    duration = int(item_str)
                # Check if it's an accidental
                elif item_str in ['+', '-']:
                    accidental = {'+': 'sharp', '-': 'flat'}[item_str]
                # Check if it's a dot
                elif item_str == '.':
                    dotted = True
            elif isinstance(item, str):
                if item in ['+', '-']:
                    accidental = {'+': 'sharp', '-': 'flat'}[item]
                elif item == '.':
                    dotted = True
            elif isinstance(item, int):
                duration = item
        
        # Use current duration if not specified
        if duration is None:
            duration = self.current_duration
        else:
            # Update current duration for following notes
            self.current_duration = duration
        
        return Note(
            pitches=[(pitch, octave, accidental)],
            duration=duration,
            dotted=dotted,
        )
    
    def rest(self, items) -> Rest:
        """
        Transform rest.
        
        Args:
            items: [duration?, dotted?]
            
        Returns:
            Rest node
        """
        duration = None
        dotted = False
        
        for item in items:
            if isinstance(item, Token):
                if item.type == 'DURATION':
                    duration = int(str(item))
                elif item.type == 'DOTTED' or str(item) == '.':
                    dotted = True
            elif isinstance(item, Tree):
                if item.data == 'duration' and item.children:
                    duration_token = item.children[0]
                    duration = int(str(duration_token))
                elif item.data == 'dotted':
                    dotted = True
            elif isinstance(item, int):
                duration = item
            elif item == '.':
                dotted = True
        
        # Use current duration if not specified
        if duration is None:
            duration = self.current_duration
        else:
            self.current_duration = duration
        
        return Rest(duration=duration, dotted=dotted)
    
    # ========================================================================
    # Chords (Multi-Pitch Notes)
    # ========================================================================
    
    def note_pitch(self, items) -> tuple:
        """
        Transform note_pitch (pitch+octave+accidental without duration).
        
        Grammar: note_pitch: NOTE_NAME ACCIDENTAL?
        
        Args:
            items: [Token(NOTE_NAME), accidental?]
            
        Returns:
            Tuple of (pitch, octave, accidental)
        """
        note_name_token = items[0]
        note_name = str(note_name_token).lower()
        
        # Parse NOTE_NAME: first char is pitch, second is octave digit
        pitch = note_name[0]
        octave = int(note_name[1])
        
        # Extract optional accidental
        accidental = None
        for item in items[1:]:
            if isinstance(item, Token):
                item_str = str(item)
                if item_str in ['+', '-']:
                    accidental = {'+': 'sharp', '-': 'flat'}[item_str]
            elif isinstance(item, str):
                if item in ['+', '-']:
                    accidental = {'+': 'sharp', '-': 'flat'}[item]
        
        return (pitch, octave, accidental)
    
    def chord(self, items) -> Note:
        """
        Transform chord into a Note with multiple pitches.
        
        Grammar: chord: note_pitch ("," note_pitch)+ ("/" DURATION DOTTED?)?
        
        Args:
            items: List of note_pitch tuples and optional duration/dotted
            
        Returns:
            Note with multiple pitches
        """
        # Collect all pitches (tuples)
        pitches = [item for item in items if isinstance(item, tuple)]
        
        # Extract optional duration and dotted
        duration = None
        dotted = False
        
        for item in items:
            if isinstance(item, Token):
                item_str = str(item)
                if item_str in ['1', '2', '4', '8', '16', '32', '64']:
                    duration = int(item_str)
                elif item_str == '.':
                    dotted = True
            elif isinstance(item, int):
                duration = item
            elif isinstance(item, str) and item == '.':
                dotted = True
        
        # Use current duration if not specified
        if duration is None:
            duration = self.current_duration
        else:
            self.current_duration = duration
        
        return Note(
            pitches=pitches,
            duration=duration,
            dotted=dotted,
        )
    
    # ========================================================================
    # Grace Notes
    # ========================================================================
    
    def grace_note(self, items) -> GraceNote:
        """
        Transform grace note.
        
        Grammar: grace_note: "~" note
        
        Args:
            items: [Note]
            
        Returns:
            GraceNote node
        """
        note = items[0] if items else None
        return GraceNote(note=note, slash=True)  # Always slashed by default
    
    # ========================================================================
    # Tuplets
    # ========================================================================
    
    def tuplet(self, items) -> Tuplet:
        """
        Transform tuplet.
        
        Grammar: tuplet: "(" event+ ")" ":" INT
        
        Args:
            items: [event1, event2, ..., ratio(Token)]
            
        Returns:
            Tuplet node
        """
        # Last item is the ratio (Token or int), everything else is events
        ratio_item = items[-1]
        if isinstance(ratio_item, Token):
            ratio = int(ratio_item.value)
        elif isinstance(ratio_item, int):
            ratio = ratio_item
        else:
            ratio = 3  # Default triplet
        
        notes = [item for item in items[:-1] if isinstance(item, (Note, Rest))]
        
        # Calculate actual duration based on tuplet convention:
        # - Triplet (3): fit into space of 2
        # - Quintuplet (5): fit into space of 4
        # - Septuplet (7): fit into space of 4
        # General rule: fit N notes into space of largest power of 2 < N
        
        if notes:
            # Get duration from first note
            first_note_duration = notes[0].duration if notes[0].duration else 4
            
            # Find space_ratio: largest power of 2 less than ratio
            space_ratio = 1
            while space_ratio * 2 < ratio:
                space_ratio *= 2
            
            # actual_duration = first_note_duration / space_ratio
            # E.g., triplet of eighth notes: 8 / 2 = 4 (quarter note)
            actual_duration = first_note_duration // space_ratio
        else:
            actual_duration = 2  # Fallback
        
        return Tuplet(notes=notes, ratio=ratio, actual_duration=actual_duration)
    
    # ========================================================================
    # Slides
    # ========================================================================
    
    def slide(self, items) -> Slide:
        """
        Grammar: slide: "<" (SLIDE_TYPE ":")? note note ">"
        
        Args:
            items: [SLIDE_TYPE(Token)?, Note, Note]
            
        Returns:
            Slide node
        """
        style = 'chromatic'  # Default
        notes = []
        
        for item in items:
            # Check if item is a Token (from SLIDE_TYPE)
            if hasattr(item, 'type') and item.type == 'SLIDE_TYPE':
                style_val = item.value
                if style_val in ['portamento', 'stepped']:
                    style = style_val
            elif isinstance(item, str) and item in ['portamento', 'stepped']:
                style = item
            elif isinstance(item, Note):
                notes.append(item)
        
        from_note = notes[0] if len(notes) > 0 else None
        to_note = notes[1] if len(notes) > 1 else None
        
        return Slide(from_note=from_note, to_note=to_note, style=style)

    # slide_type is now a TOKEN (SLIDE_TYPE), not a rule, so no transformer needed
    
    def slide_style(self, items) -> str:
        """Transform slide style."""
        return str(items[0])
    
    # ========================================================================
    # Articulations
    # ========================================================================
    
    def articulation(self, items) -> Articulation:
        """
        Transform articulation.
        
        Grammar: articulation: ":" ARTICULATION_TYPE
        
        Args:
            items: [Token(ARTICULATION_TYPE)]
            
        Returns:
            Articulation node
        """
        articulation_type = str(items[0])
        return Articulation(type=articulation_type, persistent=True)
    
    def reset_articulation(self, items) -> Reset:
        """Transform :reset directive."""
        return Reset(type='articulation')

    def reset_dynamic(self, items) -> Reset:
        """Transform @reset directive."""
        return Reset(type='dynamic')
    
    def ornament(self, items) -> Ornament:
        """
        Transform ornament.
        
        Grammar: ornament: "%" ORNAMENT_TYPE
        
        Args:
            items: [Token(ORNAMENT_TYPE)]
            
        Returns:
            Ornament node
        """
        ornament_type = str(items[0])
        # Handle abbreviations
        if ornament_type == 'tr':
            ornament_type = 'trill'
        return Ornament(type=ornament_type, note=None)
    
    def tremolo(self, items) -> Tremolo:
        """
        Transform tremolo.
        
        Grammar: tremolo: "%tremolo"
        
        Returns:
            Tremolo node
        """
        return Tremolo(note=None, rate=16)
    
    # ========================================================================
    # Dynamics
    # ========================================================================
    
    def dynamic_level(self, items) -> DynamicLevel:
        """
        Transform dynamic level.
        
        Grammar: dynamic_level: "@" DYNAMIC_LEVEL
        
        Args:
            items: [Token(DYNAMIC_LEVEL)]
            
        Returns:
            DynamicLevel node
        """
        level = str(items[0])
        return DynamicLevel(level=level)
    
    def dynamic_transition(self, items) -> DynamicTransition:
        """
        Transform dynamic transition.
        
        Grammar: dynamic_transition: "@" DYNAMIC_TRANSITION
        
        Args:
            items: [Token(DYNAMIC_TRANSITION)]
            
        Returns:
            DynamicTransition node
        """
        transition_type = str(items[0])
        # Handle abbreviation
        if transition_type == 'decresc':
            transition_type = 'diminuendo'
        return DynamicTransition(type=transition_type, target_level=None)
    
    def dynamic_accent(self, items) -> DynamicAccent:
        """
        Transform dynamic accent.
        
        Grammar: dynamic_accent: "@" DYNAMIC_ACCENT
        
        Args:
            items: [Token(DYNAMIC_ACCENT)]
            
        Returns:
            DynamicAccent node
        """
        accent_type = str(items[0])
        # Handle abbreviations
        if accent_type in ['sfz', 'sf']:
            accent_type = 'sforzando'
        return DynamicAccent(type=accent_type)
    
    # ========================================================================
    # Musical Directives
    # ========================================================================
    
    @v_args(meta=True)
    def tempo(self, items, meta) -> Tempo:
        """
        Transform tempo directive.
        
        Grammar: tempo: "(" TEMPO_KW INT ")"
        
        Args:
            items: [Token(TEMPO_KW), int] - keyword and BPM value
            meta: Lark meta object with source location information
            
        Returns:
            Tempo node
        """
        # items[0] is the keyword 'tempo!', items[1...] are INTs
        bpm = None
        for item in items:
            if isinstance(item, int) or (isinstance(item, Token) and item.type == 'INT'):
                bpm = int(item)
                break
        location = self._get_location(meta)
        return Tempo(bpm=bpm if bpm else 120)
    
    @v_args(meta=True)
    def time_signature(self, items, meta) -> TimeSignature:
        """
        Transform time signature.
        
        Grammar: time_signature: "(" TIME_KW INT INT ")"
        
        Args:
            items: [Token(TIME_KW), int, int] - keyword, numerator, denominator
            meta: Lark meta object with source location information
            
        Returns:
            TimeSignature node
        """
        # Extract integers, skipping the keyword
        ints = [int(item) for item in items if isinstance(item, (int, Token)) and (isinstance(item, int) or item.type == 'INT')]
        numerator = ints[0] if len(ints) > 0 else 4
        denominator = ints[1] if len(ints) > 1 else 4
        location = self._get_location(meta)

        return TimeSignature(
            numerator=numerator,
            denominator=denominator,
            location=location,
        )
    
    def key_root(self, items) -> list:
        """
        Transform key root (pitch letter with optional accidental).
        
        Grammar: key_root: PITCH_LETTER ACCIDENTAL?
        
        Args:
            items: [Token(PITCH_LETTER), Token(ACCIDENTAL)?]
            
        Returns:
            List of [pitch_letter, accidental?]
        """
        return list(items)
    
    def key_signature(self, items) -> KeySignature:
        """
        Transform key signature.
        
        Grammar: key_signature: "(" KEY_KW key_root ("'major" | "'minor") ")"
        
        Args:
            items: [Token(KEY_KW), Tree('key_root')/list, mode_string]
            
        Returns:
            KeySignature node
        """
        # Skip the keyword, get pitch letter with optional accidental and mode
        pitch_letter = None
        accidental = None
        mode = 'major'  # Default
        
        for item in items:
            # Handle key_root as a list [pitch_letter, accidental?]
            if isinstance(item, list):
                if len(item) >= 1:
                    pitch_letter = str(item[0]).lower()
                if len(item) >= 2:
                    acc_token = str(item[1])
                    accidental = 'sharp' if acc_token == '+' else 'flat' if acc_token == '-' else None
            else:
                item_str = str(item)
                # Skip keyword
                if item_str == 'key':
                    continue
                # Check if it's a mode
                elif 'major' in item_str or 'minor' in item_str:
                    mode = item_str.strip("'")
        
        return KeySignature(root=pitch_letter if pitch_letter else 'c', mode=mode, accidental=accidental)
    
    def pan(self, items) -> Pan:
        """
        Transform pan directive.
        
        Grammar: pan: "(" PAN_KW INT ")"
        
        Args:
            items: [Token(PAN_KW), int] - keyword and pan position (0-127)
            
        Returns:
            Pan node
        """
        # Extract integer, skipping keyword
        position = 64  # Default center
        for item in items:
            if isinstance(item, int) or (isinstance(item, Token) and item.type == 'INT'):
                position = int(item)
                break
        return Pan(position=position)
    
    # ========================================================================
    # Voices
    # ========================================================================
    # Structure Markers (removed - now handled by grammar and measures)
    # ========================================================================
    
    # ========================================================================
    # Percussion
    # ========================================================================
    
    def percussion_note(self, items) -> PercussionNote:
        """
        Transform percussion note.
        
        Args:
            items: [Token(DRUM_NAME), duration?, dotted?]
            
        Returns:
            PercussionNote node
        """
        drum_name_token = items[0]
        drum_sound = str(drum_name_token)
        
        duration = None
        dotted = False
        
        for item in items[1:]:
            if isinstance(item, Token):
                if item.type == 'DURATION':
                    duration = int(str(item))
                elif item.type == 'DOTTED' or str(item) == '.':
                    dotted = True
            elif isinstance(item, Tree):
                # Handle tree nodes from inline rules (duration, etc.)
                if item.data == 'duration' and item.children:
                    # Duration tree has the matched token as child
                    duration_token = item.children[0]
                    duration = int(str(duration_token))
                elif item.data == 'dotted':
                    dotted = True
            elif isinstance(item, int):
                duration = item
            elif item == '.':
                dotted = True
        
        # Use current duration if not specified
        if duration is None:
            duration = self.current_duration
        else:
            self.current_duration = duration
        
        return PercussionNote(
            drum_sound=drum_sound,
            duration=duration,
            dotted=dotted,
        )


# ============================================================================
# Parser Entry Point
# ============================================================================

def parse_muslang(source: str, filename: str = "<string>") -> Sequence:
    """
    Parse Muslang so with LALR algorithm, parses the source, and transforms it into an AST.
    
    The grammar uses scientific pitch notation with NO stateful octave tracking:
    - Notes specified as pitch+octave: c4/4 (C octave 4, quarter note)
    - Operator prefixes: : (articulation), @ (dynamics), % (ornaments)
    - Unambiguous LALR grammar with token priorities
    
    Args:
        source: Muslang source code as a string
        filename: Optional filename for error reporting (default: "<string>")
        
    Returns:
        Sequence node representing the entire composition
        
    Raises:
        LarkError: On syntax errors with line/column information
        
    Example:
        >>> source = '''
        ... piano: c4/4 d4/4 e4/4 f4/4
        ... '''
        >>> ast = parse_muslang(source)
        >>> print(ast.events[0].name)
        piano
    """
    # Load grammar from file
    grammar_path = Path(__file__).parent / "grammar.lark"
    
    with open(grammar_path, 'r') as f:
        grammar = f.read()
    
    # Create Lark parser with LALR algorithm (efficient, unambiguous grammar)
    parser = Lark(
        grammar,
        start='start',
        parser='lalr',  # Use LALR - the grammar is designed for it
        propagate_positions=True,  # Enable line/column tracking
        maybe_placeholders=False,
    )
    
    try:
        # Parse the source code
        parse_tree = parser.parse(source)
        
        # Transform parse tree to AST
        transformer = MuslangTransformer()
        ast = transformer.transform(parse_tree)
        
        return ast
        
    except LarkError as e:
        # Enhance error message with filename
        error_msg = f"Parse error in {filename}: {e}"
        raise LarkError(error_msg) from e


def parse_muslang_file(filepath: Path) -> Sequence:
    """
    Parse a Muslang file into an AST.
    
    Args:
        filepath: Path to the .mus file
        
    Returns:
        Sequence node representing the entire composition
        
    Raises:
        FileNotFoundError: If file doesn't exist
        LarkError: On syntax errors
        
    Example:
        >>> ast = parse_muslang_file(Path("examples/simple.mus"))
    """
    with open(filepath, 'r') as f:
        source = f.read()
    
    return parse_muslang(source, filename=str(filepath))
