"""
AST Node Definitions for Muslang

This module defines all Abstract Syntax Tree (AST) node classes used by the
Muslang music DSL compiler. All nodes are implemented as immutable dataclasses
with type hints and include source location information for error reporting.

Node Hierarchy:
    ASTNode (base)
    ├── Note (single or multi-pitch), Rest, PercussionNote
    ├── GraceNote, Tuplet
    ├── Slide
    ├── Articulation, Ornament, Tremolo, Reset
    ├── DynamicLevel, DynamicTransition, DynamicAccent, Expression
    ├── TimeSignature, KeySignature, Tempo, Pan
    ├── Voice, Instrument, Sequence
    └── Import
"""

from dataclasses import dataclass, field
from typing import Optional, List, Union, Literal, Dict


@dataclass(frozen=True)
class SourceLocation:
    """
    Source code location for error reporting.
    
    Attributes:
        line: Line number (1-indexed)
        column: Column number (1-indexed)
    """
    line: int
    column: int
    
    def __repr__(self) -> str:
        return f"<{self.line}:{self.column}>"


class ASTNode:
    """
    Base class for all AST nodes.
    
    All AST nodes should inherit from this class and include optional
    source location information for error reporting and debugging.
    
    Attributes:
        location: Optional source location where this node was defined
    """
    location: Optional[SourceLocation]
    
    def __init__(self, location: Optional[SourceLocation] = None):
        """Initialize with optional location."""
        self.location = location
    
    def __repr__(self) -> str:
        """Default repr showing class name and location"""
        loc_str = f" at {self.location}" if self.location else ""
        return f"{self.__class__.__name__}{loc_str}"


# ============================================================================
# Note and Rest Nodes
# ============================================================================

@dataclass
class Note(ASTNode):
    """
    A musical note or chord (single or multiple pitches played simultaneously).
    
    Uses scientific pitch notation where octave is ALWAYS specified (not stateful).
    For example: 
        c4/4          -> Single note C4 quarter note
        c4,e4,g4/4    -> Chord (C major triad) quarter note
    
    Represents one or more pitches with shared duration, articulation, and dynamics.
    All pitches in a chord share the same timing and modifiers.
    
    Attributes:
        pitches: List of (pitch, octave, accidental) tuples. Single note has 1 pitch, chord has 2+.
                 pitch: Note pitch (c, d, e, f, g, a, or b)
                 octave: Octave number (0-9, C4 = middle C)
                 accidental: Sharp (+), flat (-), or natural (=) modifier, or None
        duration: Note duration (1=whole, 2=half, 4=quarter, 8=eighth, etc.)
                  None means use default duration from context
        dotted: Whether the note is dotted (1.5x duration)
        start_time: Absolute start time in MIDI ticks (populated during semantic analysis)
        end_time: Absolute end time in MIDI ticks (populated during semantic analysis)
        velocity: MIDI velocity (0-127, populated during state tracking)
        articulation: Applied articulation (populated during state tracking)
        dynamic_level: Applied dynamic level (populated during state tracking)
    
    Examples:
        Single note:  pitches=[('c', 4, None)], duration=4
        Chord:        pitches=[('c', 4, None), ('e', 4, None), ('g', 4, None)], duration=4
        With accidentals: pitches=[('c', 4, 'sharp'), ('e', 4, None), ('g', 4, 'flat')], duration=4
    """
    pitches: List[tuple[Literal['c', 'd', 'e', 'f', 'g', 'a', 'b'], int, Optional[Literal['sharp', 'flat', 'natural']]]] = field(default_factory=list)
    duration: Optional[int] = None
    dotted: bool = False
    location: Optional[SourceLocation] = None
    # Timing information (populated during semantic analysis)
    start_time: Optional[float] = None  # In MIDI ticks
    end_time: Optional[float] = None    # In MIDI ticks
    # State information (populated during state tracking)
    velocity: Optional[int] = None
    articulation: Optional[str] = None
    dynamic_level: Optional[str] = None
    
    @property
    def is_chord(self) -> bool:
        """Returns True if this Note represents a chord (2+ pitches)."""
        return len(self.pitches) > 1
    
    def __repr__(self) -> str:
        def format_pitch(pitch: str, octave: int, accidental: Optional[str]) -> str:
            acc_str = {
                'sharp': '+',
                'flat': '-',
                'natural': '='
            }.get(accidental, '')
            return f"{pitch}{acc_str}{octave}"
        
        if self.pitches:
            pitch_strs = ','.join(format_pitch(p, o, a) for p, o, a in self.pitches)
        else:
            pitch_strs = ''
        
        dur_str = f"/{self.duration}" if self.duration else ''
        dot_str = '.' if self.dotted else ''
        loc_str = f" at {self.location}" if self.location else ""
        
        return f"Note({pitch_strs}{dur_str}{dot_str}){loc_str}"


@dataclass
class Rest(ASTNode):
    """
    A musical rest (silence).
    
    Attributes:
        duration: Rest duration (1=whole, 2=half, 4=quarter, etc.)
                  None means use default duration
        dotted: Whether the rest is dotted (1.5x duration)
        start_time: Absolute start time in MIDI ticks (populated during semantic analysis)
        end_time: Absolute end time in MIDI ticks (populated during semantic analysis)
    """
    duration: Optional[int] = None
    dotted: bool = False
    location: Optional[SourceLocation] = None
    # Timing information (populated during semantic analysis)
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    def __repr__(self) -> str:
        dur_str = str(self.duration) if self.duration else ''
        dot_str = '.' if self.dotted else ''
        loc_str = f" at {self.location}" if self.location else ""
        return f"Rest({dur_str}{dot_str}){loc_str}"


@dataclass
class PercussionNote(ASTNode):
    """
    A percussion/drum hit.
    
    Used for drum notation where pitch is replaced by drum sound name.
    
    Attributes:
        drum_sound: Name of the drum sound (kick, snare, hat, etc.)
        duration: Note duration (typically quarter or eighth notes for drums)
        dotted: Whether the duration is dotted
        start_time: Absolute start time in MIDI ticks (populated during semantic analysis)
        end_time: Absolute end time in MIDI ticks (populated during semantic analysis)
        velocity: MIDI velocity (0-127, populated during state tracking)
    """
    drum_sound: str
    duration: Optional[int] = None
    dotted: bool = False
    location: Optional[SourceLocation] = None
    # Timing information (populated during semantic analysis)
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    # State information (populated during state tracking)
    velocity: Optional[int] = None
    
    def __repr__(self) -> str:
        dur_str = str(self.duration) if self.duration else ''
        dot_str = '.' if self.dotted else ''
        loc_str = f" at {self.location}" if self.location else ""
        return f"Percussion({self.drum_sound}{dur_str}{dot_str}){loc_str}"


# ============================================================================
# Articulation Nodes
# ============================================================================

@dataclass
class Articulation(ASTNode):
    """
    Articulation marking that affects how notes are played.
    
    Uses colon prefix (:) in source: :legato, :staccato, :tenuto, :marcato, :natural
    Articulations control note duration and attack characteristics.
    
    Attributes:
        type: Type of articulation (legato, staccato, tenuto, marcato, natural)
        persistent: If True, applies to all following notes until changed
                   If False, applies only to the immediately following note
        scope: Where this articulation was declared (composition, instrument, or voice)
    
    Examples:
        :legato   -> Smooth, connected notes
        :staccato -> Short, detached notes
        :tenuto   -> Full value, slight emphasis
        :marcato  -> Strong accent
        :natural  -> Natural/default articulation (no duration alteration)
    """
    type: Literal['legato', 'staccato', 'tenuto', 'marcato', 'natural']
    persistent: bool = True
    scope: Literal['composition', 'instrument', 'voice'] = 'voice'
    location: Optional[SourceLocation] = None
    
    def __repr__(self) -> str:
        persist_str = "" if self.persistent else " (one-shot)"
        loc_str = f" at {self.location}" if self.location else ""
        return f"Articulation(.{self.type}{persist_str}){loc_str}"


@dataclass
class Ornament(ASTNode):
    """
    Musical ornament (embellishment).
    
    Uses percent prefix (%) in source: %trill, %mordent, %turn
    Ornaments are decorative note patterns that expand into sequences of fast notes.
    
    Attributes:
        type: Type of ornament (trill, mordent, turn)
        note: The principal note that is ornamented (attached during semantic analysis)
    
    Examples:
        %trill   -> Rapid alternation with upper neighbor
        %mordent -> Principal note, lower neighbor, principal
        %turn    -> Upper, principal, lower, principal
    """
    type: Literal['trill', 'mordent', 'turn']
    note: Optional[Note] = None
    
    def __repr__(self) -> str:
        note_str = f" on {self.note}" if self.note else ""
        loc_str = f" at {self.location}" if self.location else ""
        return f"Ornament(.{self.type}{note_str}){loc_str}"


@dataclass
class Tremolo(ASTNode):
    """
    Tremolo effect (rapid repetition of a note or alternation between notes).
    
    Uses percent prefix in source: %tremolo
    The tremolo marking causes rapid repetition at a specified rate.
    
    Attributes:
        note: The note to apply tremolo to (attached during semantic analysis)
        rate: Repetition rate (notes per quarter note, default 16 for 16th notes)
    """
    note: Optional[Note] = None
    rate: int = 16
    
    def __repr__(self) -> str:
        note_str = f" on {self.note}" if self.note else ""
        loc_str = f" at {self.location}" if self.location else ""
        return f"Tremolo(.tremolo{note_str}){loc_str}"


@dataclass
class Reset(ASTNode):
    """
    Reset articulation or dynamics by popping from their respective stacks.
    
    Uses colon prefix for articulation, at-sign for dynamics:
      :reset -> Pop from articulation stack
      @reset -> Pop from dynamics stack
    
    Attributes:
        type: What to reset
              'articulation' - pop from articulation stack (undo last articulation change)
              'dynamic' - pop from dynamics stack (undo last dynamic change)
    
    Examples:
        :reset -> Undo last articulation change
        @reset -> Undo last dynamic change
    """
    type: Literal['articulation', 'dynamic'] = 'articulation'
    
    def __repr__(self) -> str:
        reset_str = "" if self.type == 'full' else f".{self.type}"
        loc_str = f" at {self.location}" if self.location else ""
        return f"Reset({reset_str or '.'}){loc_str}"


# ============================================================================
# Dynamic Nodes
# ============================================================================

@dataclass
class DynamicLevel(ASTNode):
    """
    Absolute dynamic level (volume).
    
    Uses at-sign prefix (@) in source: @pp, @p, @mp, @mf, @f, @ff
    Sets the volume level for following notes.
    
    Attributes:
        level: Dynamic marking (pp=pianissimo, p=piano, mp=mezzo-piano,
               mf=mezzo-forte, f=forte, ff=fortissimo)
        scope: Where this dynamic was declared (composition, instrument, or voice)
    
    Examples:
        @pp -> Very soft (pianissimo)
        @mf -> Medium loud (mezzo-forte)
        @ff -> Very loud (fortissimo)
    """
    level: Literal['pp', 'p', 'mp', 'mf', 'f', 'ff']
    scope: Literal['composition', 'instrument', 'voice'] = 'voice'
    
    def __repr__(self) -> str:
        loc_str = f" at {self.location}" if self.location else ""
        return f"Dynamic(.{self.level}){loc_str}"


@dataclass
class DynamicTransition(ASTNode):
    """
    Gradual dynamic change over multiple notes.
    
    Uses at-sign prefix (@) in source: @crescendo, @diminuendo
    Crescendo (getting louder) or diminuendo (getting softer).
    
    Attributes:
        type: Type of transition (crescendo or diminuendo)
        target_level: Optional target dynamic level to reach (if None, continues indefinitely)
        scope: Where this transition was declared (composition, instrument, or voice)
    
    Examples:
        @crescendo -> Gradually get louder
        @diminuendo -> Gradually get softer
    """
    type: Literal['crescendo', 'diminuendo']
    target_level: Optional[Literal['pp', 'p', 'mp', 'mf', 'f', 'ff']] = None
    scope: Literal['composition', 'instrument', 'voice'] = 'voice'
    
    def __repr__(self) -> str:
        target_str = f" to {self.target_level}" if self.target_level else ""
        loc_str = f" at {self.location}" if self.location else ""
        return f"DynamicTransition(.{self.type}{target_str}){loc_str}"


@dataclass
class DynamicAccent(ASTNode):
    """
    One-time dynamic accent on a single note.
    
    Uses at-sign prefix (@) in source: @sforzando, @forte-piano
    Accents apply to only the immediately following note.
    
    Attributes:
        type: Type of accent
              'sforzando' - sudden strong accent (sf, sfz)
              'marcato' - stressed, emphasized accent
              'forte-piano' - loud then immediately soft (fp)
        scope: Where this accent was declared (composition, instrument, or voice)
    
    Examples:
        @sforzando -> Sudden strong accent
        @forte-piano -> Loud attack, immediately soft
    """
    type: Literal['sforzando', 'marcato', 'forte-piano']
    scope: Literal['composition', 'instrument', 'voice'] = 'voice'
    
    def __repr__(self) -> str:
        loc_str = f" at {self.location}" if self.location else ""
        return f"Accent(.{self.type}){loc_str}"


@dataclass
class Expression(ASTNode):
    """
    Expression text marking (dolce, espressivo, etc.).
    
    Expression markings provide performance direction beyond basic dynamics.
    In MIDI, these map to CC#11 (expression controller).
    
    Attributes:
        text: Expression text
        cc_value: MIDI CC#11 value (0-127), if specified
    """
    text: str
    cc_value: Optional[int] = None
    
    def __repr__(self) -> str:
        cc_str = f" (CC={self.cc_value})" if self.cc_value is not None else ""
        loc_str = f" at {self.location}" if self.location else ""
        return f"Expression({self.text}{cc_str}){loc_str}"


# ============================================================================
# Rhythm Modifier Nodes
# ============================================================================

@dataclass
class GraceNote(ASTNode):
    """
    Grace note (ornamental quick note before the main note).
    
    Grace notes are played very quickly, "stealing" time from the following note.
    
    Attributes:
        note: The grace note to play
        slash: If True, this is an acciaccatura (struck grace note with slash)
               If False, this is an appoggiatura (leaning grace note)
    """
    note: Note
    slash: bool = True
    
    def __repr__(self) -> str:
        slash_str = "/" if self.slash else ""
        loc_str = f" at {self.location}" if self.location else ""
        return f"GraceNote(~{slash_str}{self.note}){loc_str}"


@dataclass
class Tuplet(ASTNode):
    """
    Tuplet grouping (triplets, quintuplets, etc.).
    
    Uses parentheses in source: (c4/8 d4/8 e4/8):3
    Tuplets fit a different number of notes into the space of a normal grouping.
    For example, a triplet fits 3 notes into the space of 2.
    
    Attributes:
        notes: List of notes in the tuplet
        ratio: Number of notes to fit (3 for triplet, 5 for quintuplet, etc.)
        actual_duration: The duration value that the tuplet occupies
                        (e.g., 2 means the tuplet takes the space of a half note)
    
    Example:
        (c4/8 d4/8 e4/8):3 -> Triplet of three eighth notes
    """
    notes: List[Note] = field(default_factory=list)
    ratio: int = 3
    actual_duration: int = 2
    location: Optional[SourceLocation] = None
    
    def __repr__(self) -> str:
        num_notes = len(self.notes)
        loc_str = f" at {self.location}" if self.location else ""
        return f"Tuplet({num_notes} notes, {self.ratio}:{self.actual_duration}){loc_str}"


# ============================================================================
# Phrase Grouping Nodes
# ============================================================================

@dataclass
class Slide(ASTNode):
    """
    Slide/glissando between two notes.
    
    Uses angle brackets in source: <note note> or <portamento: note note>
    Slides the pitch from one note to another over the duration.
    NOW UNAMBIGUOUS - no conflict with octave operators!
    
    Attributes:
        from_note: Starting note
        to_note: Ending note
        style: How to perform the slide:
               'chromatic' - smooth pitch bend (MIDI pitch wheel) [default]
               'stepped' - individual chromatic steps
               'portamento' - smooth slide using MIDI portamento (CC#65)
    
    Examples:
        <c4/4 c5/4>              -> Chromatic slide from C4 to C5
        <portamento: c4/4 g4/4>  -> Portamento slide
        <stepped: c4/4 c5/4>     -> Stepped chromatic notes
    """
    from_note: Note
    to_note: Note
    style: Literal['chromatic', 'stepped', 'portamento'] = 'chromatic'
    
    def __repr__(self) -> str:
        style_str = f".{self.style} " if self.style != 'chromatic' else ""
        loc_str = f" at {self.location}" if self.location else ""
        return f"Slide(<{style_str}{self.from_note} -> {self.to_note}>){loc_str}"


@dataclass
class Measure(ASTNode):
    """
    Measure grouping (events between bar lines).
    
    Groups events that occur within a single measure, separated by | bar lines.
    Measures enable validation of note durations against the active time signature.
    
    Attributes:
        events: List of events in this measure
        measure_number: Measure number for tracking and error reporting (1-indexed)
        start_time: Absolute start time in MIDI ticks (populated during semantic analysis)
        end_time: Absolute end time in MIDI ticks (populated during semantic analysis)
    
    Example:
        V1: c4/4 d4/4 e4/4 f4/4 | g4/2 a4/2 |
            ^-- Measure 1 --^   ^-Measure 2-^
    """
    events: List[ASTNode] = field(default_factory=list)
    measure_number: Optional[int] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    location: Optional[SourceLocation] = None
    
    def __repr__(self) -> str:
        num_events = len(self.events)
        measure_str = f"#{self.measure_number} " if self.measure_number else ""
        loc_str = f" at {self.location}" if self.location else ""
        return f"Measure({measure_str}{num_events} events){loc_str}"


# ============================================================================
# Structural Nodes
# ============================================================================

@dataclass
class Instrument(ASTNode):
    """
    Instrument part containing events.
    
    Represents a single instrument track with all its musical events.
    Can contain multiple voices.
    
    Attributes:
        name: Instrument name (maps to General MIDI program number)
        events: List of musical events for this instrument
        voices: Dictionary mapping voice numbers to their event lists
                (for polyphonic parts like piano left/right hand)
        defaults_sequence: List of (voice_index, cumulative_defaults) tuples
                          tracking instrument-level defaults before each voice
    """
    name: str
    events: List[ASTNode] = field(default_factory=list)
    voices: dict[int, List[ASTNode]] = field(default_factory=dict)
    defaults_sequence: List[tuple[int, Dict[str, any]]] = field(default_factory=list)
    
    def __repr__(self) -> str:
        num_events = len(self.events)
        num_voices = len(self.voices)
        voice_str = f", {num_voices} voices" if num_voices > 0 else ""
        loc_str = f" at {self.location}" if self.location else ""
        return f"Instrument({self.name}: {num_events} events{voice_str}){loc_str}"


@dataclass
class Voice(ASTNode):
    """
    Voice declaration for polyphonic parts.
    
    Voices allow multiple melodic lines within a single instrument.
    For example, piano parts often use V1 for right hand and V2 for left hand.
    
    Attributes:
        number: Voice number (1, 2, 3, etc.)
        events: Musical events in this voice
    """
    number: int
    events: List[ASTNode] = field(default_factory=list)
    
    def __repr__(self) -> str:
        num_events = len(self.events)
        loc_str = f" at {self.location}" if self.location else ""
        return f"Voice(V{self.number}: {num_events} events){loc_str}"


@dataclass
class Sequence(ASTNode):
    """
    Sequence of events (represents entire composition or a sub-sequence).
    
    For top-level compositions, uses instruments dict for natural grouping.
    For sub-sequences, uses events list.
    
    Attributes:
        instruments: Dictionary mapping instrument names to Instrument nodes (top-level)
        events: List of events for sub-sequences
        composition_defaults: Dictionary of composition-level default settings
        location: Optional source location
    """
    instruments: Dict[str, 'Instrument'] = field(default_factory=dict)
    events: List[ASTNode] = field(default_factory=list)
    composition_defaults: Dict[str, any] = field(default_factory=dict)
    location: Optional[SourceLocation] = None
    
    def __repr__(self) -> str:
        if self.instruments:
            num_insts = len(self.instruments)
            loc_str = f" at {self.location}" if self.location else ""
            return f"Sequence({num_insts} instruments){loc_str}"
        else:
            num_events = len(self.events)
            loc_str = f" at {self.location}" if self.location else ""
            return f"Sequence({num_events} events){loc_str}"


# ============================================================================
# Musical Context Nodes
# ============================================================================

@dataclass
class TimeSignature(ASTNode):
    """
    Time signature (meter) directive.
    
    Specifies how many beats per measure and which note value gets the beat.
    
    Attributes:
        numerator: Number of beats per measure (e.g., 4 in 4/4 time)
        denominator: Note value that gets one beat (e.g., 4 means quarter note)
        scope: Where this time signature was declared (composition, instrument, or voice)
    """
    numerator: int
    denominator: int
    scope: Literal['composition', 'instrument', 'voice'] = 'voice'
    location: Optional[SourceLocation] = None
    
    def __repr__(self) -> str:
        loc_str = f" at {self.location}" if self.location else ""
        return f"TimeSignature({self.numerator}/{self.denominator}){loc_str}"


@dataclass
class KeySignature(ASTNode):
    """
    Key signature directive.
    
    Specifies the key (root note and mode) which determines default accidentals.
    
    Attributes:
        root: Root note of the key (c, d, e, f, g, a, or b)
        mode: Mode of the key ('major' or 'minor')
        accidental: Optional accidental for the root (sharp or flat)
        scope: Where this key signature was declared (composition, instrument, or voice)
    """
    root: Literal['c', 'd', 'e', 'f', 'g', 'a', 'b']
    mode: Literal['major', 'minor']
    accidental: Optional[Literal['sharp', 'flat']] = None
    scope: Literal['composition', 'instrument', 'voice'] = 'voice'
    
    def __repr__(self) -> str:
        acc_str = {'sharp': '#', 'flat': 'b'}.get(self.accidental, '')
        loc_str = f" at {self.location}" if self.location else ""
        return f"KeySignature({self.root.upper()}{acc_str} {self.mode}){loc_str}"


@dataclass
class Tempo(ASTNode):
    """
    Tempo directive (speed).
    
    Sets the playback tempo in beats per minute.
    
    Attributes:
        bpm: Beats per minute (typically 40-240)
        scope: Where this tempo was declared (composition, instrument, or voice)
    """
    bpm: int
    scope: Literal['composition', 'instrument', 'voice'] = 'voice'
    
    def __repr__(self) -> str:
        loc_str = f" at {self.location}" if self.location else ""
        return f"Tempo({self.bpm} BPM){loc_str}"


@dataclass
class Pan(ASTNode):
    """
    Pan (stereo position) directive.
    
    Controls the left-right stereo position using MIDI CC#10.
    
    Attributes:
        position: Pan position (0=full left, 64=center, 127=full right)
        scope: Where this pan was declared (composition, instrument, or voice)
    """
    position: int
    scope: Literal['composition', 'instrument', 'voice'] = 'voice'
    
    def __repr__(self) -> str:
        loc_str = f" at {self.location}" if self.location else ""
        return f"Pan({self.position}){loc_str}"


@dataclass
class Import(ASTNode):
    """
    Import directive to include another .mus file.
    
    Allows composition to be split across multiple files.
    
    Attributes:
        filepath: Path to the file to import (relative or absolute)
    """
    filepath: str
    
    def __repr__(self) -> str:
        loc_str = f" at {self.location}" if self.location else ""
        return f"Import({self.filepath}){loc_str}"


# ============================================================================
# Type Aliases for Union Types
# ============================================================================

# Union type for all nodes that can appear in an event sequence
EventNode = Union[
    Note, Rest, PercussionNote,
    GraceNote, Tuplet,
    Slide, Measure,
    Articulation, Ornament, Tremolo, Reset,
    DynamicLevel, DynamicTransition, DynamicAccent, Expression,
    TimeSignature, KeySignature, Tempo, Pan,
    Voice, Instrument,
    Import
]
