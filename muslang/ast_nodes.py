"""
AST Node Definitions for Muslang

This module defines all Abstract Syntax Tree (AST) node classes used by the
Muslang music DSL compiler. All nodes are implemented as immutable dataclasses
with type hints and include source location information for error reporting.

Node Hierarchy:
    ASTNode (base)
    ├── Note, Rest, Chord, PercussionNote
    ├── GraceNote, Tuplet
    ├── Slur, Slide
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
    A single musical note with scientific pitch notation.
    
    Uses scientific pitch notation where octave is ALWAYS specified (not stateful).
    For example: c4/4 = C octave 4, quarter note
    
    Represents a pitch with octave, duration, accidental, and modifiers.
    
    Attributes:
        pitch: Note pitch (c, d, e, f, g, a, or b)
        octave: Octave number (0-9, C4 = middle C)
                Always specified in source - NO stateful octave tracking!
        duration: Note duration (1=whole, 2=half, 4=quarter, 8=eighth, etc.)
                  None means use default duration from context
        dotted: Whether the note is dotted (1.5x duration)
        accidental: Sharp (+), flat (-), or natural (=) accidental modifier
        tied: Whether this note is tied to the next note (~)
        start_time: Absolute start time in MIDI ticks (populated during semantic analysis)
        end_time: Absolute end time in MIDI ticks (populated during semantic analysis)
        velocity: MIDI velocity (0-127, populated during state tracking)
        articulation: Applied articulation (populated during state tracking)
        dynamic_level: Applied dynamic level (populated during state tracking)
    
    Examples:
        c4/4   -> C4 quarter note (pitch=c, octave=4, duration=4)
        d5+/8. -> D#5 dotted eighth (pitch=d, octave=5, duration=8, dotted=True, accidental=sharp)
        e4~    -> E4 tied (pitch=e, octave=4, tied=True)
    """
    pitch: Literal['c', 'd', 'e', 'f', 'g', 'a', 'b']
    octave: int
    duration: Optional[int] = None
    dotted: bool = False
    accidental: Optional[Literal['sharp', 'flat', 'natural']] = None
    tied: bool = False
    location: Optional[SourceLocation] = None
    # Timing information (populated during semantic analysis)
    start_time: Optional[float] = None  # In MIDI ticks
    end_time: Optional[float] = None    # In MIDI ticks
    # State information (populated during state tracking)
    velocity: Optional[int] = None
    articulation: Optional[str] = None
    dynamic_level: Optional[str] = None
    
    def __repr__(self) -> str:
        acc_str = {
            'sharp': '+',
            'flat': '-',
            'natural': '='
        }.get(self.accidental, '')
        
        dur_str = str(self.duration) if self.duration else ''
        dot_str = '.' if self.dotted else ''
        tie_str = '~' if self.tied else ''
        loc_str = f" at {self.location}" if self.location else ""
        
        return f"Note({self.pitch}{acc_str}{self.octave}{dur_str}{dot_str}{tie_str}){loc_str}"


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
class Chord(ASTNode):
    """
    Multiple notes played simultaneously.
    
    Attributes:
        notes: List of notes in the chord (must have at least 2 notes)
        start_time: Absolute start time in MIDI ticks (populated during semantic analysis)
        end_time: Absolute end time in MIDI ticks (populated during semantic analysis)
    """
    notes: List[Note] = field(default_factory=list)
    # Timing information (populated during semantic analysis)
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    def __repr__(self) -> str:
        note_strs = '/'.join(str(n.pitch) + str(n.octave) for n in self.notes)
        loc_str = f" at {self.location}" if self.location else ""
        return f"Chord({note_strs}){loc_str}"


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
    
    Uses colon prefix (:) in source: :legato, :staccato, :tenuto, :marcato
    Articulations control note duration and attack characteristics.
    
    Attributes:
        type: Type of articulation (legato, staccato, tenuto, marcato)
        persistent: If True, applies to all following notes until changed
                   If False, applies only to the immediately following note
    
    Examples:
        :legato   -> Smooth, connected notes
        :staccato -> Short, detached notes
        :tenuto   -> Full value, slight emphasis
        :marcato  -> Strong accent
    """
    type: Literal['legato', 'staccato', 'tenuto', 'marcato']
    persistent: bool = True
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
    Reset articulation to default (natural) state.
    
    Uses colon prefix in source: :reset
    
    Attributes:
        type: What to reset (currently only 'natural' supported)
              'natural' - reset articulation to natural
              'full' - reset both articulation and dynamics
    
    Example:
        :reset -> Return to natural articulation
    """
    type: Literal['natural', 'full'] = 'full'
    
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
    
    Examples:
        @pp -> Very soft (pianissimo)
        @mf -> Medium loud (mezzo-forte)
        @ff -> Very loud (fortissimo)
    """
    level: Literal['pp', 'p', 'mp', 'mf', 'f', 'ff']
    
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
    
    Examples:
        @crescendo -> Gradually get louder
        @diminuendo -> Gradually get softer
    """
    type: Literal['crescendo', 'diminuendo']
    target_level: Optional[Literal['pp', 'p', 'mp', 'mf', 'f', 'ff']] = None
    
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
    
    Examples:
        @sforzando -> Sudden strong accent
        @forte-piano -> Loud attack, immediately soft
    """
    type: Literal['sforzando', 'marcato', 'forte-piano']
    
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
    
    def __repr__(self) -> str:
        num_notes = len(self.notes)
        loc_str = f" at {self.location}" if self.location else ""
        return f"Tuplet({num_notes} notes, {self.ratio}:{self.actual_duration}){loc_str}"


# ============================================================================
# Phrase Grouping Nodes
# ============================================================================

@dataclass
class Slur(ASTNode):
    """
    Slurred phrase grouping.
    
    Notes under a slur are played smoothly connected (legato) with minimal
    separation between notes. In MIDI, this uses CC#68 (legato) and note overlap.
    
    Attributes:
        notes: List of notes to slur together (minimum 2 notes)
    """
    notes: List[Note] = field(default_factory=list)
    
    def __repr__(self) -> str:
        num_notes = len(self.notes)
        loc_str = f" at {self.location}" if self.location else ""
        return f"Slur({{{num_notes} notes}}){loc_str}"


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
    """
    name: str
    events: List[ASTNode] = field(default_factory=list)
    voices: dict[int, List[ASTNode]] = field(default_factory=dict)
    
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
        location: Optional source location
    """
    instruments: Dict[str, 'Instrument'] = field(default_factory=dict)
    events: List[ASTNode] = field(default_factory=list)
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
    """
    numerator: int
    denominator: int
    
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
    """
    root: Literal['c', 'd', 'e', 'f', 'g', 'a', 'b']
    mode: Literal['major', 'minor']
    accidental: Optional[Literal['sharp', 'flat']] = None
    
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
    """
    bpm: int
    
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
    """
    position: int
    
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
    Note, Rest, Chord, PercussionNote,
    GraceNote, Tuplet,
    Slur, Slide,
    Articulation, Ornament, Tremolo, Reset,
    DynamicLevel, DynamicTransition, DynamicAccent, Expression,
    TimeSignature, KeySignature, Tempo, Pan,
    Voice, Instrument,
    Import
]
