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
- Graceful handling of optional elements (accidentals, durations, dots, ties)
- Operator prefixes: : (articulation), @ (dynamics), % (ornaments)
"""

from pathlib import Path
from typing import Optional, List, Any
from lark import Lark, Transformer, Token, Tree
from lark.exceptions import LarkError

from .ast_nodes import (
    Note, Rest, Chord, PercussionNote,
    GraceNote, Tuplet,
    Slur, Slide,
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
    
    def composition(self, items) -> Sequence:
        """
        Transform composition into Sequence with instruments dict.
        
        Multiple declarations of the same instrument are merged by
        concatenating their events in order of appearance.
        
        Args:
            items: List of Instrument nodes
            
        Returns:
            Sequence node with instruments dict
        """
        instruments = {}
        for inst in items:
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
                instruments[inst.name] = Instrument(
                    name=inst.name,
                    events=merged_events,
                    voices=merged_voices
                )
            else:
                instruments[inst.name] = inst
        
        return Sequence(instruments=instruments)
    
    def instrument(self, items) -> Instrument:
        """
        Transform instrument declaration, grouping events by voice.
        
        ALL notes must be in voices. Only directives (tempo, time signature, etc.)
        are allowed at the instrument level.
        
        Args:
            items: [Token(INSTRUMENT_NAME), events_list]
            
        Returns:
            Instrument node with name, events, and voices dict
        """
        name_token = items[0]
        events_list = items[1] if len(items) > 1 else []
        instrument_name = str(name_token)
        
        # Reset state for each instrument
        self.current_duration = DEFAULT_NOTE_DURATION
        self.current_voice = None
        
        # Allowed directive types (not notes/chords/percussion)
        DIRECTIVE_TYPES = (Tempo, TimeSignature, KeySignature, Pan, 
                          Articulation, DynamicLevel, DynamicTransition, 
                          DynamicAccent, Reset, Ornament, Tremolo, Expression)
        
        # Group events by voice
        voices = {}
        non_voice_events = []
        current_voice = None
        
        for event in events_list:
            if isinstance(event, Voice):
                # Voice declaration - switch context
                current_voice = event.number
                if current_voice not in voices:
                    voices[current_voice] = []
            elif current_voice is not None:
                # We're in a voice context - add to that voice
                voices[current_voice].append(event)
            else:
                # No voice context - only directives allowed
                if isinstance(event, DIRECTIVE_TYPES):
                    non_voice_events.append(event)
                elif isinstance(event, (Note, Rest, Chord, PercussionNote, Slur, Slide, GraceNote, Tuplet)):
                    raise ValueError(
                        f"Error in instrument '{instrument_name}': "
                        f"All notes must be in a voice (e.g., V1:). "
                        f"Found {type(event).__name__} outside of voice context."
                    )
                else:
                    non_voice_events.append(event)
        
        # Require at least one voice
        if not voices:
            raise ValueError(
                f"Error in instrument '{instrument_name}': "
                f"At least one voice (e.g., V1:) is required."
            )
        
        return Instrument(
            name=instrument_name,
            events=non_voice_events,
            voices=voices,
        )
    
    def events(self, items) -> List[Any]:
        """
        Transform events list.
        
        Args:
            items: List of event nodes
            
        Returns:
            List of event nodes (filtering out None values from bar lines)
        """
        return [item for item in items if item is not None]
    
    # ========================================================================
    # Notes and Basic Rhythm
    # ========================================================================
    
    def note(self, items) -> Note:
        """
        Transform note with scientific pitch notation.
        
        Grammar: note: NOTE_NAME accidental? ("/" duration dotted?)? tie?
        NOTE_NAME format: pitch+octave (e.g., c4, d5, a3)
        
        Args:
            items: [Token(NOTE_NAME), accidental?, duration?, dotted?, tie?]
            
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
        tied = False
        
        for item in items[1:]:
            if isinstance(item, Tree):
                # Handle tree nodes from inline rules (duration, etc.)
                if item.data == 'duration' and item.children:
                    # Duration tree has the matched token as child
                    duration_token = item.children[0]
                    duration = int(str(duration_token))
                elif item.data == 'dotted':
                    dotted = True
                elif item.data == 'tie':
                    tied = True
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
                # Check if it's a tie
                elif item_str == '~':
                    tied = True
            elif isinstance(item, str):
                if item in ['+', '-']:
                    accidental = {'+': 'sharp', '-': 'flat'}[item]
                elif item == '.':
                    dotted = True
                elif item == '~':
                    tied = True
            elif isinstance(item, int):
                duration = item
        
        # Use current duration if not specified
        if duration is None:
            duration = self.current_duration
        else:
            # Update current duration for following notes
            self.current_duration = duration
        
        return Note(
            pitch=pitch,
            octave=octave,
            duration=duration,
            dotted=dotted,
            accidental=accidental,
            tied=tied,
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
    # Chords
    # ========================================================================
    
    def chord(self, items) -> Chord:
        """
        Transform chord.
        
        Args:
            items: List of Note nodes
            
        Returns:
            Chord node containing all notes
        """
        notes = [item for item in items if isinstance(item, Note)]
        return Chord(notes=notes)
    
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
            items: [event1, event2, ..., ratio(int)]
            
        Returns:
            Tuplet node
        """
        # Last item is the ratio (int), everything else is events
        ratio = items[-1] if items and isinstance(items[-1], int) else 3
        notes = [item for item in items[:-1] if isinstance(item, (Note, Chord, Rest))]
        
        # Calculate actual duration from the notes
        # For now, default to space of 2 notes
        actual_duration = 2
        
        return Tuplet(notes=notes, ratio=ratio, actual_duration=actual_duration)
    
    # ========================================================================
    # Slurs
    # ========================================================================
    
    def slur(self, items) -> Slur:
        """
        Transform slur.
        
        Args:
            items: List of event nodes
            
        Grammar: slur: "{" event+ "}"
        
        Args:
            items: List of event nodes
            
        Returns:
            Slur node
        """
        # Collect all notes from events (filter out non-notes)
        notes = [item for item in items if isinstance(item, (Note, Chord))]
        return Slur(notes=notes)
    
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
    
    def reset(self, items) -> Reset:
        """
        Transform reset directive.
        
        Grammar: reset: ":reset"
        
        Args:
            items: []
            
        Returns:
            Reset node
        """
        return Reset(type='full')
    
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
    
    def tempo(self, items) -> Tempo:
        """
        Transform tempo directive.
        
        Grammar: tempo: "(" TEMPO_KW INT ")"
        
        Args:
            items: [Token(TEMPO_KW), int] - keyword and BPM value
            
        Returns:
            Tempo node
        """
        # items[0] is the keyword 'tempo!', items[1...] are INTs
        bpm = None
        for item in items:
            if isinstance(item, int) or (isinstance(item, Token) and item.type == 'INT'):
                bpm = int(item)
                break
        return Tempo(bpm=bpm if bpm else 120)
    
    def time_signature(self, items) -> TimeSignature:
        """
        Transform time signature.
        
        Grammar: time_signature: "(" TIME_KW INT INT ")"
        
        Args:
            items: [Token(TIME_KW), int, int] - keyword, numerator, denominator
            
        Returns:
            TimeSignature node
        """
        # Extract integers, skipping the keyword
        ints = [int(item) for item in items if isinstance(item, (int, Token)) and (isinstance(item, int) or item.type == 'INT')]
        numerator = ints[0] if len(ints) > 0 else 4
        denominator = ints[1] if len(ints) > 1 else 4
        return TimeSignature(numerator=numerator, denominator=denominator)
    
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
    
    def voice(self, items) -> Voice:
        """
        Transform voice declaration.
        
        Grammar: voice: VOICE ":"
        
        Args:
            items: [VOICE token] - voice identifier (e.g., "V1", "V2")
            
        Returns:
            Voice node (events will be populated by instrument)
        """
        # Extract number from VOICE token (e.g., "V1" -> 1)
        voice_token = str(items[0])
        voice_number = int(voice_token[1:])  # Skip the 'V' prefix
        self.current_voice = voice_number
        return Voice(number=voice_number, events=[])
    
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
    
    # ========================================================================
    # Structure Markers
    # ========================================================================
    
    def bar_line(self, items) -> None:
        """
        Transform bar line (just ignore it).
        
        Bar lines are structural markers for readability but don't affect
        the semantic meaning of the music.
        
        Returns:
            None
        """
        return None


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
