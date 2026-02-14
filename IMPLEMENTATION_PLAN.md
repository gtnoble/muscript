# Muslang Implementation Plan

Detailed implementation guide for the Muslang music DSL compiler.

## Overview

**Goal**: Build a Python-based music composition DSL that compiles to MIDI files, with extensive articulation, dynamics, and expressive notation support.

**Tech Stack**:
- Python 3.10+
- Lark parser (LALR with transformer)
- midiutil for MIDI file generation
- pytest for testing

**Architecture**:
```
Source (.mus) → Lexer/Parser (Lark) → AST → Semantic Analysis → MIDI Events → MIDI File (.mid)
```

---

## Phase 1: Project Foundation (Days 1-2)

### 1.1 Project Structure Setup

**Create directory structure**:
```
muslang/
├── muslang/
│   ├── __init__.py
│   ├── ast_nodes.py          # AST node definitions
│   ├── grammar.lark          # Lark grammar
│   ├── parser.py             # Parser & transformer
│   ├── semantics.py          # Semantic analysis
│   ├── articulations.py      # Articulation mapping
│   ├── drums.py              # Percussion mapping
│   ├── theory.py             # Music theory (keys, scales)
│   ├── midi_gen.py           # MIDI file generation
│   ├── cli.py                # Command-line interface
│   └── config.py             # Configuration & constants
├── tests/
│   ├── __init__.py
│   ├── test_parser.py
│   ├── test_semantics.py
│   ├── test_articulations.py
│   ├── test_midi_gen.py
│   ├── test_drums.py
│   ├── test_theory.py
│   └── test_integration.py
├── examples/
│   ├── basic_melody.mus
│   ├── articulation_showcase.mus
│   ├── dynamics_demo.mus
│   ├── rhythm_complex.mus
│   ├── ornaments_demo.mus
│   ├── drum_beat.mus
│   ├── piano_voices.mus
│   └── orchestral.mus
├── docs/
│   ├── syntax_reference.md
│   ├── articulation_guide.md
│   ├── rhythm_guide.md
│   ├── ornaments_guide.md
│   └── percussion_guide.md
├── pyproject.toml
├── README.md
└── IMPLEMENTATION_PLAN.md
```

**pyproject.toml**:
```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_backend"

[project]
name = "muslang"
version = "0.1.0"
description = "A music composition DSL with extensive articulation support"
requires-python = ">=3.10"
dependencies = [
    "lark>=1.1.0",
    "midiutil>=1.2.1",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "mido>=1.3.0",  # For MIDI analysis in tests
]

[project.scripts]
muslang = "muslang.cli:main"
```

**Tasks**:
- [x] Create directory structure
- [x] Write pyproject.toml with dependencies
- [x] Create __init__.py files
- [x] Write basic README.md with project description
- [x] Initialize git repository

### 1.2 Configuration & Constants

**muslang/config.py**:
```python
# MIDI configuration
DEFAULT_MIDI_PPQ = 480  # Pulses per quarter note
DEFAULT_TEMPO = 120     # BPM
DEFAULT_VELOCITY = 85   # mezzo-forte

# Default articulation
NATURAL_DURATION_PERCENT = 92  # 92% of note value
DEFAULT_NOTE_DURATION = 1      # Whole note

# Dynamic level velocities
VELOCITY_PP = 40
VELOCITY_P = 55
VELOCITY_MP = 70
VELOCITY_MF = 85
VELOCITY_F = 100
VELOCITY_FF = 115

# Accent boosts
SFORZANDO_BOOST = 20
MARCATO_BOOST = 30
FORTE_PIANO_BOOST = 35

# Articulation durations (as percentage of note value)
STACCATO_DURATION = 55
LEGATO_DURATION = 100  # With overlap
TENUTO_DURATION = 100
MARCATO_DURATION = 90

# Crescendo/diminuendo velocity change per note
DYNAMIC_TRANSITION_STEP = 6

# Grace note duration (in ticks, relative to PPQ)
GRACE_NOTE_DURATION_RATIO = 0.05  # 5% of quarter note

# Tremolo repetition rate (notes per quarter note)
TREMOLO_RATE = 16  # 16th notes

# MIDI CC numbers
CC_MODULATION = 1
CC_EXPRESSION = 11
CC_PAN = 10
CC_SUSTAIN = 64
CC_LEGATO = 68
CC_PORTAMENTO_TIME = 5
CC_PORTAMENTO_SWITCH = 65

# General MIDI defaults
GM_DRUM_CHANNEL = 9  # 0-indexed (channel 10 in 1-indexed)
```

**Tasks**:
- [x] Create config.py with all constants
- [x] Add docstrings explaining each constant

---

## Phase 2: AST Definitions (Day 2-3)

### 2.1 Core AST Node Classes

**muslang/ast_nodes.py**:

Design principles:
- Use dataclasses for clean, immutable nodes
- Each node has a `__repr__` for debugging
- Include source location info (line, column) for error messages
- Use type hints throughout

**Node hierarchy**:
```
ASTNode (base)
├── Note
├── Rest
├── Chord
├── GraceNote
├── Tuplet
├── Slur
├── Slide
├── PercussionNote
├── Articulation
├── Ornament
├── Tremolo
├── Reset
├── DynamicLevel
├── DynamicTransition
├── DynamicAccent
├── Expression
├── TimeSignature
├── KeySignature
├── Tempo
├── Pan
├── Voice
├── Instrument
├── Variable
├── VariableReference
├── Repeat
├── Import
└── Sequence
```

**Implementation order**:
1. **Base classes**: ASTNode, SourceLocation
2. **Basic notes**: Note, Rest, Chord
3. **Rhythm modifiers**: GraceNote, Tuplet
4. **Phrase groupings**: Slur, Slide
5. **Articulations**: Articulation, Ornament, Tremolo, Reset
6. **Dynamics**: DynamicLevel, DynamicTransition, DynamicAccent, Expression
7. **Musical context**: TimeSignature, KeySignature, Tempo, Pan
8. **Structure**: Voice, Instrument, Sequence
9. **Programming constructs**: Variable, VariableReference, Repeat, Import
10. **Percussion**: PercussionNote

**Key node examples**:

```python
from dataclasses import dataclass, field
from typing import Optional, List, Union, Literal
from enum import Enum

@dataclass
class SourceLocation:
    """Source code location for error reporting"""
    line: int
    column: int
    
@dataclass
class ASTNode:
    """Base class for all AST nodes"""
    location: Optional[SourceLocation] = None
    
@dataclass
class Note(ASTNode):
    """A single musical note"""
    pitch: Literal['c', 'd', 'e', 'f', 'g', 'a', 'b']
    octave: int
    duration: Optional[int] = None  # 1=whole, 2=half, 4=quarter, etc.
    dotted: bool = False
    accidental: Optional[Literal['sharp', 'flat', 'natural']] = None
    tied: bool = False
    
@dataclass
class Articulation(ASTNode):
    """Articulation marking"""
    type: Literal['legato', 'staccato', 'tenuto', 'marcato']
    persistent: bool = True
    
@dataclass
class DynamicLevel(ASTNode):
    """Absolute dynamic level"""
    level: Literal['pp', 'p', 'mp', 'mf', 'f', 'ff']
    
@dataclass
class DynamicTransition(ASTNode):
    """Gradual dynamic change (crescendo/diminuendo)"""
    type: Literal['crescendo', 'diminuendo']
    
@dataclass
class GraceNote(ASTNode):
    """Grace note (ornamental quick note)"""
    note: Note
    
@dataclass
class Tuplet(ASTNode):
    """Tuplet grouping (triplets, quintuplets, etc.)"""
    notes: List[Note]
    ratio: int  # 3 for triplet, 5 for quintuplet
    actual_duration: int  # Space they occupy
    
@dataclass  
class Slur(ASTNode):
    """Slurred phrase grouping"""
    notes: List[Note]
    
@dataclass
class Slide(ASTNode):
    """Slide/glissando between two notes"""
    from_note: Note
    to_note: Note
    style: Literal['chromatic', 'stepped', 'portamento'] = 'chromatic'
    
@dataclass
class Ornament(ASTNode):
    """Musical ornament (trill, mordent, turn)"""
    type: Literal['trill', 'mordent', 'turn']
    note: Note
    
@dataclass
class Instrument(ASTNode):
    """Instrument part with events"""
    name: str
    events: List[ASTNode]
    voices: dict[int, List[ASTNode]] = field(default_factory=dict)
```

**Tasks**:
- [ ] Create base ASTNode and SourceLocation classes
- [ ] Implement all note/rest related nodes
- [ ] Implement articulation nodes
- [ ] Implement dynamic nodes
- [ ] Implement rhythm modifier nodes (tuplet, grace)
- [ ] Implement phrase grouping nodes (slur, slide)
- [ ] Implement ornament nodes
- [ ] Implement structural nodes (instrument, voice, sequence)
- [ ] Implement programming nodes (variable, repeat)
- [ ] Add __repr__ methods for debugging
- [ ] Add type hints throughout
- [ ] Write unit tests for node creation

---

## Phase 3: Grammar Definition (Days 3-5)

### 3.1 Lark Grammar Structure

**muslang/grammar.lark**:

Design principles:
- LALR parser for efficiency
- Clear, unambiguous rules
- Whitespace-insensitive (spaces, newlines, tabs)
- Comments as terminal
- Left-to-right evaluation (Alda-style)

**Grammar sections**:
1. **Terminals**: Basic tokens (pitch, number, operators)
2. **Notes & Rhythm**: Note syntax, durations, rests
3. **Accidentals**: Sharp/flat notation
4. **Articulations**: Prefix modifiers
5. **Dynamics**: Level and transition markers
6. **Ornaments**: Trill, mordent, turn
7. **Groupings**: Slurs, slides, tuplets
8. **Directives**: Tempo, time signature, key signature, pan
9. **Structure**: Instruments, voices
10. **Programming**: Variables, repeats
11. **Comments**: Hash-style comments

**Grammar outline**:
```lark
?start: composition

composition: instrument+

instrument: INSTRUMENT_NAME ":" events

events: event+

?event: note
      | rest
      | chord
      | grace_note
      | tuplet
      | slur
      | slide
      | articulation
      | dynamic_level
      | dynamic_transition
      | dynamic_accent
      | ornament
      | tremolo
      | reset
      | octave_change
      | tempo
      | time_signature
      | key_signature
      | pan
      | voice
      | variable_def
      | variable_ref
      | repeat
      | bar_line

// Notes
note: PITCH accidental? duration? dotted? tie?
PITCH: "c" | "d" | "e" | "f" | "g" | "a" | "b"
accidental: "+" | "-"
duration: INT
dotted: "."
tie: "~"

// Chords
chord: note ("/" note)+

// Grace notes
grace_note: "~" note

// Tuplets
tuplet: "[" note+ "]" ":" INT

// Rests
rest: "r" duration? dotted?

// Slurs
slur: "{" event+ "}"

// Slides
slide: "<" slide_modifier? note note ">"
slide_modifier: "." SLIDE_TYPE
SLIDE_TYPE: "portamento" | "stepped"

// Articulations
articulation: "." ARTICULATION_TYPE
ARTICULATION_TYPE: "legato" | "staccato" | "tenuto" | "marcato"

reset: "." "natural"?  // "." alone or ".natural"

// Dynamics
dynamic_level: "." DYNAMIC_LEVEL
DYNAMIC_LEVEL: "pp" | "p" | "mp" | "mf" | "f" | "ff"

dynamic_transition: "." DYNAMIC_TRANSITION
DYNAMIC_TRANSITION: "crescendo" | "diminuendo" | "decresc"

dynamic_accent: "." DYNAMIC_ACCENT
DYNAMIC_ACCENT: "sforzando" | "forte-piano"

// Ornaments
ornament: "." ORNAMENT_TYPE
ORNAMENT_TYPE: "trill" | "mordent" | "turn"

tremolo: "." "tremolo"

// Octave
octave_change: "o" INT | ">" | "<"

// Directives
tempo: "(" "tempo!" INT ")"
time_signature: "(" "time" INT INT ")"
key_signature: "(" "key" PITCH ("'major" | "'minor") ")"
pan: "(" "pan" INT ")"

// Voices
voice: "V" INT ":"

// Variables
variable_def: VARNAME "=" "[" event+ "]"
variable_ref: "$" VARNAME
VARNAME: /[a-zA-Z_][a-zA-Z0-9_]*/

// Repeat
repeat: "[" event+ "]" "*" INT

// Bar lines
bar_line: "|"

// Percussion
percussion_note: DRUM_NAME duration? dotted?
DRUM_NAME: "kick" | "snare" | "hat" | "hihat" | "crash" | "ride" 
         | "tom1" | "tom2" | "tom3" | "rimshot" | "clap"

// Instrument names
INSTRUMENT_NAME: /[a-zA-Z][a-zA-Z0-9_-]*/

// Comments
COMMENT: "#" /[^\n]*/

// Whitespace
%import common.INT
%import common.WS
%ignore WS
%ignore COMMENT
```

**Grammar development strategy**:
1. Start with minimal grammar (notes, rests, instruments)
2. Test parsing basic melodies
3. Incrementally add features (articulations → dynamics → ornaments → etc.)
4. Test each addition with examples
5. Refine ambiguities and conflicts

**Tasks**:
- [ ] Create basic grammar skeleton (notes, durations, instruments)
- [ ] Add articulation syntax
- [ ] Add dynamics syntax
- [ ] Add ornament syntax
- [ ] Add grouping syntax (slurs, slides, tuplets)
- [ ] Add directive syntax (tempo, time sig, key sig)
- [ ] Add voice syntax
- [ ] Add variable and repeat syntax
- [ ] Add percussion syntax
- [ ] Add comment handling
- [ ] Test grammar with lark-standalone tool
- [ ] Write parser smoke tests

---

## Phase 4: Parser Implementation (Days 5-7)

### 4.1 Lark Transformer

**muslang/parser.py**:

The transformer converts Lark parse tree into AST nodes.

**Structure**:
```python
from lark import Lark, Transformer, Token
from muslang.ast_nodes import *
from muslang.config import *

class MuslangTransformer(Transformer):
    """Transforms Lark parse tree to AST"""
    
    def __init__(self):
        super().__init__()
        self.current_octave = 4
        self.current_duration = DEFAULT_NOTE_DURATION
        
    # Note transformations
    def note(self, items):
        """Transform note rule to Note AST node"""
        pitch = items[0].value
        accidental = None
        duration = None
        dotted = False
        tied = False
        
        for item in items[1:]:
            if isinstance(item, Token) and item.type == 'ACCIDENTAL':
                accidental = 'sharp' if item.value == '+' else 'flat'
            elif isinstance(item, int):
                duration = item
            elif item == 'dotted':
                dotted = True
            elif item == 'tie':
                tied = True
                
        return Note(
            pitch=pitch,
            octave=self.current_octave,
            duration=duration or DEFAULT_NOTE_DURATION,
            dotted=dotted,
            accidental=accidental,
            tied=tied
        )
    
    def chord(self, items):
        """Transform chord to Chord AST node"""
        return Chord(notes=items)
    
    def grace_note(self, items):
        """Transform grace note"""
        return GraceNote(note=items[0])
    
    def tuplet(self, items):
        """Transform tuplet"""
        notes = items[:-1]
        ratio = items[-1]
        return Tuplet(notes=notes, ratio=ratio, actual_duration=2)
    
    # Articulation transformations
    def articulation(self, items):
        """Transform articulation marker"""
        artic_type = items[0].value
        return Articulation(type=artic_type, persistent=True)
    
    def reset(self, items):
        """Transform reset marker"""
        if len(items) > 0 and items[0] == 'natural':
            return Reset(type='natural')
        return Reset(type='full')
    
    # Dynamic transformations
    def dynamic_level(self, items):
        """Transform dynamic level"""
        level = items[0].value
        return DynamicLevel(level=level)
    
    def dynamic_transition(self, items):
        """Transform crescendo/diminuendo"""
        trans_type = items[0].value
        return DynamicTransition(type=trans_type)
    
    # Ornament transformations
    def ornament(self, items):
        """Transform ornament"""
        ornament_type = items[0].value
        return Ornament(type=ornament_type, note=None)  # Note attached in semantic pass
    
    # Grouping transformations
    def slur(self, items):
        """Transform slur grouping"""
        return Slur(notes=items)
    
    def slide(self, items):
        """Transform slide"""
        style = 'chromatic'
        notes = []
        
        for item in items:
            if isinstance(item, str) and item in ['portamento', 'stepped']:
                style = item
            else:
                notes.append(item)
        
        return Slide(from_note=notes[0], to_note=notes[1], style=style)
    
    # Directive transformations
    def tempo(self, items):
        """Transform tempo directive"""
        bpm = int(items[0])
        return Tempo(bpm=bpm)
    
    def time_signature(self, items):
        """Transform time signature"""
        numerator = int(items[0])
        denominator = int(items[1])
        return TimeSignature(numerator=numerator, denominator=denominator)
    
    def key_signature(self, items):
        """Transform key signature"""
        root = items[0].value
        mode = items[1].value.strip("'")
        return KeySignature(root=root, mode=mode)
    
    # Octave transformations
    def octave_change(self, items):
        """Transform octave change"""
        token = items[0]
        if token == '>':
            self.current_octave += 1
        elif token == '<':
            self.current_octave -= 1
        else:
            self.current_octave = int(token)
        return None  # Octave change is stateful, not an event
    
    # Voice transformations
    def voice(self, items):
        """Transform voice declaration"""
        voice_num = int(items[0])
        return Voice(number=voice_num, events=[])
    
    # Instrument transformations
    def instrument(self, items):
        """Transform instrument section"""
        name = items[0].value
        events = [e for e in items[1:] if e is not None]
        return Instrument(name=name, events=events, voices={})
    
    def composition(self, items):
        """Transform top-level composition"""
        return Sequence(events=items)

def parse_muslang(source: str) -> Sequence:
    """Parse muslang source code into AST"""
    with open('muslang/grammar.lark', 'r') as f:
        grammar = f.read()
    
    parser = Lark(grammar, parser='lalr', transformer=MuslangTransformer())
    try:
        ast = parser.parse(source)
        return ast
    except Exception as e:
        # Add better error handling
        raise SyntaxError(f"Parse error: {e}")
```

**Parser state management**:
- Track current octave (changes with `o4`, `>`, `<`)
- Track voice context (when inside V1:, V2:)
- Track articulation context for applying to notes
- Build symbol table for variables

**Tasks**:
- [ ] Create MuslangTransformer class
- [ ] Implement note/rest/chord transformations
- [ ] Implement articulation transformations
- [ ] Implement dynamic transformations
- [ ] Implement ornament transformations
- [ ] Implement grouping transformations (slur, slide, tuplet)
- [ ] Implement directive transformations
- [ ] Implement voice transformations
- [ ] Implement variable/repeat transformations
- [ ] Implement octave state tracking
- [ ] Add error handling with line/column info
- [ ] Write parser unit tests

---

## Phase 5: Semantic Analysis (Days 7-10)

### 5.1 Semantic Analyzer

**muslang/semantics.py**:

The semantic analyzer:
1. Validates AST correctness (type checking, range checking)
2. Resolves references (variables, key signatures)
3. Expands constructs (repeats, ornaments, tremolo, tuplets)
4. Calculates absolute timing
5. Tracks state (articulations, dynamics, octave)
6. Applies musical transformations (key sig accidentals, grace note timing)

**Structure**:
```python
from muslang.ast_nodes import *
from muslang.config import *
from muslang.theory import KeySignatureInfo, expand_ornament
from typing import List, Dict

class SemanticAnalyzer:
    """Semantic analysis and AST transformation"""
    
    def __init__(self):
        self.symbol_table: Dict[str, List[ASTNode]] = {}
        self.current_time_sig = TimeSignature(4, 4)
        self.current_key_sig = None
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
                expanded.extend(node.sequence)
            return Sequence(events=expanded)
        
        return self._transform_children(node, self._expand_repeats)
    
    def _apply_key_signatures(self, node: ASTNode) -> ASTNode:
        """Apply key signature accidentals"""
        if isinstance(node, KeySignature):
            self.current_key_sig = node
            return node
        
        elif isinstance(node, Note):
            if self.current_key_sig and node.accidental is None:
                # Apply key signature
                key_info = KeySignatureInfo(self.current_key_sig.root, 
                                           self.current_key_sig.mode)
                if key_info.affects_pitch(node.pitch):
                    node.accidental = key_info.get_accidental(note.pitch)
        
        return self._transform_children(node, self._apply_key_signatures)
    
    def _expand_ornaments(self, node: ASTNode) -> ASTNode:
        """Expand ornaments into note sequences"""
        # This handles .trill, .mordent, .turn
        # Look for (Ornament, Note) pairs and expand
        if isinstance(node, Sequence):
            expanded = []
            i = 0
            while i < len(node.events):
                event = node.events[i]
                
                if isinstance(event, Ornament) and i + 1 < len(node.events):
                    next_event = node.events[i + 1]
                    if isinstance(next_event, Note):
                        # Expand ornament
                        notes = expand_ornament(event, next_event, self.current_key_sig)
                        expanded.extend(notes)
                        i += 2  # Skip both ornament and note
                        continue
                
                expanded.append(event)
                i += 1
            
            node.events = expanded
        
        return self._transform_children(node, self._expand_ornaments)
    
    def _calculate_timing(self, node: ASTNode) -> ASTNode:
        """Calculate absolute timing for all events"""
        # Walk through events, accumulate timing
        # Assign start_time and end_time to each note
        # This is complex - needs to handle:
        # - Note durations
        # - Tuplets (scale timing)
        # - Grace notes (steal time)
        # - Tempo changes
        # - Time signature changes
        pass
    
    def _track_state(self, node: ASTNode) -> ASTNode:
        """Track articulation and dynamic state"""
        # Walk through events in order
        # Track current articulation (legato, staccato, etc.)
        # Track current dynamic level and transitions
        # Assign these to each note
        pass
    
    def _error(self, message: str):
        """Record an error"""
        self.errors.append(message)
    
    def _warning(self, message: str):
        """Record a warning"""
        self.warnings.append(message)
```

**Key algorithms**:
- **Timing calculation**: Walk event stream, accumulate durations accounting for time signature, tuplets, grace notes
- **State tracking**: Maintain state machine for articulations and dynamics, apply to each note
- **Ornament expansion**: Generate note sequences based on ornament type and current key
- **Variable resolution**: Symbol table lookup and inline expansion

**Tasks**:
- [ ] Create SemanticAnalyzer class
- [ ] Implement AST validation
- [ ] Implement variable resolution
- [ ] Implement repeat expansion
- [ ] Implement key signature application
- [ ] Implement ornament expansion (trill, mordent, turn)
- [ ] Implement tremolo expansion
- [ ] Implement tuplet timing calculation
- [ ] Implement grace note timing
- [ ] Implement absolute timing calculation
- [ ] Implement state tracking (articulations, dynamics)
- [ ] Add error collection and reporting
- [ ] Write semantic analysis unit tests

---

## Phase 6: Music Theory Support (Days 8-9)

### 6.1 Key Signatures and Scales

**muslang/theory.py**:

```python
from typing import List, Literal
from muslang.ast_nodes import Note

# Key signature definitions
MAJOR_KEYS = {
    'C': [],
    'G': ['f+'],
    'D': ['f+', 'c+'],
    'A': ['f+', 'c+', 'g+'],
    'E': ['f+', 'c+', 'g+', 'd+'],
    'B': ['f+', 'c+', 'g+', 'd+', 'a+'],
    'F': ['b-'],
    'Bb': ['b-', 'e-'],
    'Eb': ['b-', 'e-', 'a-'],
    'Ab': ['b-', 'e-', 'a-', 'd-'],
    'Db': ['b-', 'e-', 'a-', 'd-', 'g-'],
}

MINOR_KEYS = {
    'a': [],
    'e': ['f+'],
    'b': ['f+', 'c+'],
    # ... etc
}

class KeySignatureInfo:
    """Information about a key signature"""
    
    def __init__(self, root: str, mode: str):
        self.root = root
        self.mode = mode
        self.accidentals = self._get_accidentals()
    
    def _get_accidentals(self) -> List[str]:
        """Get list of accidentals for this key"""
        if self.mode == 'major':
            return MAJOR_KEYS.get(self.root, [])
        else:
            return MINOR_KEYS.get(self.root, [])
    
    def affects_pitch(self, pitch: str) -> bool:
        """Check if key signature affects this pitch"""
        for acc in self.accidentals:
            if acc[0] == pitch:
                return True
        return False
    
    def get_accidental(self, pitch: str) -> str:
        """Get accidental for pitch in this key"""
        for acc in self.accidentals:
            if acc[0] == pitch:
                return 'sharp' if acc[1] == '+' else 'flat'
        return None

def expand_ornament(ornament, note: Note, key_sig) -> List[Note]:
    """Expand ornament into note sequence"""
    if ornament.type == 'trill':
        # Trill between note and upper neighbor
        upper = _get_upper_neighbor(note, key_sig)
        # Generate alternating notes at 32nd note rate
        trill_notes = []
        for i in range(8):  # 8 32nd notes
            if i % 2 == 0:
                trill_notes.append(Note(note.pitch, note.octave, 32))
            else:
                trill_notes.append(upper)
        return trill_notes
    
    elif ornament.type == 'mordent':
        # Main note, lower neighbor, main note
        lower = _get_lower_neighbor(note, key_sig)
        return [
            Note(note.pitch, note.octave, 32),
            lower,
            Note(note.pitch, note.octave, note.duration),
        ]
    
    elif ornament.type == 'turn':
        # Upper, main, lower, main
        upper = _get_upper_neighbor(note, key_sig)
        lower = _get_lower_neighbor(note, key_sig)
        return [upper, note, lower, note]

def _get_upper_neighbor(note: Note, key_sig) -> Note:
    """Get upper scale neighbor of note"""
    # Scale-aware neighbor calculation
    pass

def _get_lower_neighbor(note: Note, key_sig) -> Note:
    """Get lower scale neighbor of note"""
    pass
```

**Tasks**:
- [ ] Define key signature mappings (major and minor)
- [ ] Implement KeySignatureInfo class
- [ ] Implement scale degree calculations
- [ ] Implement ornament expansion functions
- [ ] Implement neighbor tone calculations
- [ ] Write music theory unit tests

### 6.2 Percussion Mapping

**muslang/drums.py**:

```python
# General MIDI Drum Map (Channel 10)
DRUM_MAP = {
    'kick': 36,          # Bass Drum 1
    'kick2': 35,         # Bass Drum 2 (acoustic)
    'snare': 38,         # Acoustic Snare
    'snare2': 40,        # Electric Snare
    'hat': 42,           # Closed Hi-Hat
    'hihat': 42,         # Alias
    'openhat': 46,       # Open Hi-Hat
    'crash': 49,         # Crash Cymbal 1
    'crash2': 57,        # Crash Cymbal 2
    'ride': 51,          # Ride Cymbal 1
    'tom1': 48,          # Hi Tom
    'tom2': 45,          # Low Tom
    'tom3': 43,          # High Floor Tom
    'tom4': 41,          # Low Floor Tom
    'rimshot': 37,       # Side Stick / Rimshot
    'clap': 39,          # Hand Clap
    'cowbell': 56,       # Cowbell
    'tambourine': 54,    # Tambourine
    'splash': 55,        # Splash Cymbal
    'china': 52,         # Chinese Cymbal
}

def get_drum_midi_note(drum_name: str) -> int:
    """Get MIDI note number for drum name"""
    if drum_name not in DRUM_MAP:
        raise ValueError(f"Unknown drum name: {drum_name}")
    return DRUM_MAP[drum_name]

def is_percussion_instrument(instrument_name: str) -> bool:
    """Check if instrument name is a percussion instrument"""
    return instrument_name.lower() in ['drums', 'percussion', 'kit']
```

**Tasks**:
- [ ] Define complete drum map
- [ ] Implement drum name lookup
- [ ] Add percussion instrument detection
- [ ] Write drum mapping unit tests

---

## Phase 7: Articulation Mapping (Days 10-11)

### 7.1 Articulation System

**muslang/articulations.py**:

```python
from muslang.config import *
from muslang.ast_nodes import Note, Articulation, DynamicLevel
from dataclasses import dataclass
from typing import Optional

@dataclass
class ArticulationState:
    """Current articulation state"""
    type: str = 'natural'
    duration_percent: int = NATURAL_DURATION_PERCENT
    
@dataclass
class DynamicState:
    """Current dynamic state"""
    level: str = 'mf'
    velocity: int = VELOCITY_MF
    transition_active: Optional[str] = None  # 'crescendo' or 'diminuendo'
    target_velocity: Optional[int] = None
    
class ArticulationMapper:
    """Maps articulations to MIDI parameters"""
    
    def __init__(self):
        self.artic_state = ArticulationState()
        self.dynamic_state = DynamicState()
    
    def process_articulation(self, artic: Articulation):
        """Update articulation state"""
        if artic.type == 'staccato':
            self.artic_state.type = 'staccato'
            self.artic_state.duration_percent = STACCATO_DURATION
        elif artic.type == 'legato':
            self.artic_state.type = 'legato'
            self.artic_state.duration_percent = LEGATO_DURATION
        elif artic.type == 'tenuto':
            self.artic_state.type = 'tenuto'
            self.artic_state.duration_percent = TENUTO_DURATION
        elif artic.type == 'marcato':
            self.artic_state.type = 'marcato'
            self.artic_state.duration_percent = MARCATO_DURATION
    
    def process_reset(self, reset_type: str):
        """Reset articulation and/or dynamics"""
        if reset_type == 'natural':
            # Reset articulation only
            self.artic_state = ArticulationState()
        elif reset_type == 'full':
            # Reset both
            self.artic_state = ArticulationState()
            self.dynamic_state = DynamicState()
    
    def process_dynamic_level(self, level: str):
        """Update dynamic level"""
        velocity_map = {
            'pp': VELOCITY_PP,
            'p': VELOCITY_P,
            'mp': VELOCITY_MP,
            'mf': VELOCITY_MF,
            'f': VELOCITY_F,
            'ff': VELOCITY_FF,
        }
        self.dynamic_state.level = level
        self.dynamic_state.velocity = velocity_map[level]
        self.dynamic_state.target_velocity = velocity_map[level]
    
    def process_dynamic_transition(self, trans_type: str):
        """Start crescendo or diminuendo"""
        self.dynamic_state.transition_active = trans_type
    
    def get_note_duration(self, base_duration_ticks: int) -> int:
        """Calculate actual note duration based on articulation"""
        return int(base_duration_ticks * self.artic_state.duration_percent / 100)
    
    def get_note_velocity(self, accent_type: Optional[str] = None) -> int:
        """Calculate note velocity based on dynamic state and accents"""
        velocity = self.dynamic_state.velocity
        
        # Apply one-shot accents
        if accent_type == 'sforzando':
            velocity = min(127, velocity + SFORZANDO_BOOST)
        elif accent_type == 'marcato':
            velocity = min(127, velocity + MARCATO_BOOST)
        elif accent_type == 'forte-piano':
            velocity = min(127, velocity + FORTE_PIANO_BOOST)
        
        # Apply crescendo/diminuendo
        if self.dynamic_state.transition_active:
            if self.dynamic_state.transition_active == 'crescendo':
                self.dynamic_state.velocity = min(
                    self.dynamic_state.target_velocity,
                    self.dynamic_state.velocity + DYNAMIC_TRANSITION_STEP
                )
            elif self.dynamic_state.transition_active == 'diminuendo':
                self.dynamic_state.velocity = max(
                    self.dynamic_state.target_velocity,
                    self.dynamic_state.velocity - DYNAMIC_TRANSITION_STEP
                )
            
            velocity = self.dynamic_state.velocity
        
        return min(127, max(0, velocity))
    
    def should_add_legato_cc(self) -> bool:
        """Check if legato CC#68 should be sent"""
        return self.artic_state.type == 'legato'
```

**Tasks**:
- [ ] Create ArticulationState and DynamicState classes
- [ ] Implement ArticulationMapper class
- [ ] Implement articulation processing
- [ ] Implement dynamic level processing
- [ ] Implement crescendo/diminuendo tracking
- [ ] Implement note duration calculation
- [ ] Implement velocity calculation with accents
- [ ] Write articulation mapping unit tests

---

## Phase 8: MIDI Generation (Days 11-14)

### 8.1 MIDI Event Generator

**muslang/midi_gen.py**:

```python
from midiutil import MIDIFile
from muslang.ast_nodes import *
from muslang.articulations import ArticulationMapper
from muslang.drums import get_drum_midi_note, is_percussion_instrument
from muslang.config import *
from typing import Dict, List, Tuple

# General MIDI instrument map (subset)
INSTRUMENT_MAP = {
    'piano': 0,
    'guitar': 24,
    'bass': 32,
    'violin': 40,
    'viola': 41,
    'cello': 42,
    'trumpet': 56,
    'trombone': 57,
    'flute': 73,
    'clarinet': 71,
    # ... more instruments
}

class MIDIGenerator:
    """Generate MIDI file from AST"""
    
    def __init__(self, ppq: int = DEFAULT_MIDI_PPQ):
        self.ppq = ppq
        self.midi = None
        self.current_time = 0
        self.channel_counter = 0
        self.instrument_channels: Dict[str, int] = {}
    
    def generate(self, ast: Sequence, output_path: str):
        """Generate MIDI file from AST"""
        # Count instruments for tracks
        instruments = [node for node in ast.events if isinstance(node, Instrument)]
        num_tracks = len(instruments)
        
        # Create MIDI file
        self.midi = MIDIFile(num_tracks, deinterleave=False)
        self.midi.addTempo(0, 0, DEFAULT_TEMPO)
        
        # Process each instrument
        for track_num, instrument in enumerate(instruments):
            self._process_instrument(track_num, instrument)
        
        # Write MIDI file
        with open(output_path, 'wb') as f:
            self.midi.writeFile(f)
    
    def _process_instrument(self, track_num: int, instrument: Instrument):
        """Process an instrument and generate MIDI events"""
        # Assign MIDI channel
        if is_percussion_instrument(instrument.name):
            channel = GM_DRUM_CHANNEL
        else:
            channel = self._get_next_channel()
            # Set program (instrument sound)
            program = INSTRUMENT_MAP.get(instrument.name.lower(), 0)
            self.midi.addProgramChange(track_num, channel, 0, program)
        
        self.instrument_channels[instrument.name] = channel
        
        # Initialize state
        mapper = ArticulationMapper()
        current_time = 0
        
        # Process events
        for event in instrument.events:
            current_time = self._process_event(
                track_num, channel, event, current_time, mapper
            )
    
    def _process_event(self, track, channel, event, time, mapper):
        """Process a single event and return new time"""
        
        if isinstance(event, Note):
            return self._generate_note(track, channel, event, time, mapper)
        
        elif isinstance(event, Rest):
            # Advance time without generating note
            duration = self._duration_to_ticks(event.duration, event.dotted)
            return time + duration
        
        elif isinstance(event, Chord):
            # Generate all notes at same time
            max_duration = 0
            for note in event.notes:
                self._generate_note(track, channel, note, time, mapper)
                duration = self._duration_to_ticks(note.duration, note.dotted)
                max_duration = max(max_duration, duration)
            return time + max_duration
        
        elif isinstance(event, Articulation):
            mapper.process_articulation(event)
            return time
        
        elif isinstance(event, DynamicLevel):
            mapper.process_dynamic_level(event.level)
            return time
        
        elif isinstance(event, DynamicTransition):
            mapper.process_dynamic_transition(event.type)
            return time
        
        elif isinstance(event, Reset):
            mapper.process_reset(event.type)
            return time
        
        elif isinstance(event, Tempo):
            self.midi.addTempo(track, time / self.ppq, event.bpm)
            return time
        
        elif isinstance(event, TimeSignature):
            self.midi.addTimeSignature(track, time / self.ppq, 
                                      event.numerator, event.denominator, 24)
            return time
        
        elif isinstance(event, Pan):
            self.midi.addControllerEvent(track, channel, time / self.ppq, 
                                        CC_PAN, event.position)
            return time
        
        elif isinstance(event, Slur):
            # Enable legato CC at start
            self.midi.addControllerEvent(track, channel, time / self.ppq, 
                                        CC_LEGATO, 127)
            
            # Generate slurred notes with overlap
            slur_time = time
            for i, note in enumerate(event.notes):
                slur_time = self._generate_note(track, channel, note, 
                                               slur_time, mapper, overlap=True)
            
            # Disable legato CC at end
            self.midi.addControllerEvent(track, channel, slur_time / self.ppq, 
                                        CC_LEGATO, 0)
            return slur_time
        
        elif isinstance(event, Slide):
            return self._generate_slide(track, channel, event, time, mapper)
        
        elif isinstance(event, PercussionNote):
            midi_note = get_drum_midi_note(event.drum_sound)
            duration = self._duration_to_ticks(event.duration, event.dotted)
            velocity = mapper.get_note_velocity()
            
            self.midi.addNote(track, channel, midi_note, 
                            time / self.ppq, duration / self.ppq, velocity)
            return time + duration
        
        # ... handle other event types
        
        return time
    
    def _generate_note(self, track, channel, note, time, mapper, 
                      overlap=False, accent=None):
        """Generate MIDI note on/off events"""
        # Calculate MIDI note number
        midi_note = self._note_to_midi(note)
        
        # Calculate duration
        base_duration = self._duration_to_ticks(note.duration, note.dotted)
        actual_duration = mapper.get_note_duration(base_duration)
        
        # Calculate velocity
        velocity = mapper.get_note_velocity(accent)
        
        # Add note
        self.midi.addNote(track, channel, midi_note,
                         time / self.ppq, actual_duration / self.ppq, velocity)
        
        # Add legato CC if needed
        if mapper.should_add_legato_cc():
            self.midi.addControllerEvent(track, channel, time / self.ppq, 
                                        CC_LEGATO, 127)
        
        # Advance time
        if overlap:
            # For slurred notes, advance by slightly less than full duration
            return time + int(actual_duration * 0.95)
        else:
            return time + base_duration
    
    def _generate_slide(self, track, channel, slide, time, mapper):
        """Generate pitch bend events for slide"""
        from_midi = self._note_to_midi(slide.from_note)
        to_midi = self._note_to_midi(slide.to_note)
        
        duration = self._duration_to_ticks(slide.from_note.duration, 
                                          slide.from_note.dotted)
        
        if slide.style == 'chromatic':
            # Generate pitch bend events
            semitones = to_midi - from_midi
            bend_range = 2  # ±2 semitones
            
            # Calculate bend values
            steps = 20  # Number of bend steps
            for i in range(steps + 1):
                bend_time = time + (duration * i // steps)
                bend_value = int(8192 + (8192 * semitones * i / (steps * bend_range)))
                bend_value = max(0, min(16383, bend_value))
                
                self.midi.addPitchWheelEvent(track, channel, 
                                           bend_time / self.ppq, bend_value)
            
            # Add the note at original pitch
            velocity = mapper.get_note_velocity()
            self.midi.addNote(track, channel, from_midi,
                            time / self.ppq, duration / self.ppq, velocity)
            
            # Reset pitch bend
            self.midi.addPitchWheelEvent(track, channel, 
                                        (time + duration) / self.ppq, 8192)
        
        elif slide.style == 'stepped':
            # Generate intermediate notes
            from_midi = self._note_to_midi(slide.from_note)
            to_midi = self._note_to_midi(slide.to_note)
            step = 1 if to_midi > from_midi else -1
            
            velocity = mapper.get_note_velocity()
            step_duration = duration // abs(to_midi - from_midi)
            
            current_pitch = from_midi
            current_time = time
            while current_pitch != to_midi:
                self.midi.addNote(track, channel, current_pitch,
                                current_time / self.ppq, step_duration / self.ppq, 
                                velocity)
                current_pitch += step
                current_time += step_duration
            
            # Final note
            self.midi.addNote(track, channel, to_midi,
                            current_time / self.ppq, step_duration / self.ppq, 
                            velocity)
        
        elif slide.style == 'portamento':
            # Use portamento CC
            self.midi.addControllerEvent(track, channel, time / self.ppq, 
                                        CC_PORTAMENTO_TIME, 64)
            self.midi.addControllerEvent(track, channel, time / self.ppq, 
                                        CC_PORTAMENTO_SWITCH, 127)
            
            # Generate notes
            velocity = mapper.get_note_velocity()
            self.midi.addNote(track, channel, from_midi,
                            time / self.ppq, duration / self.ppq, velocity)
            
            # Disable portamento
            self.midi.addControllerEvent(track, channel, 
                                        (time + duration) / self.ppq, 
                                        CC_PORTAMENTO_SWITCH, 0)
        
        return time + duration
    
    def _note_to_midi(self, note: Note) -> int:
        """Convert note to MIDI note number"""
        pitch_map = {'c': 0, 'd': 2, 'e': 4, 'f': 5, 'g': 7, 'a': 9, 'b': 11}
        midi_note = (note.octave + 1) * 12 + pitch_map[note.pitch]
        
        if note.accidental == 'sharp':
            midi_note += 1
        elif note.accidental == 'flat':
            midi_note -= 1
        
        return midi_note
    
    def _duration_to_ticks(self, duration: int, dotted: bool) -> int:
        """Convert note duration to MIDI ticks"""
        # duration: 1=whole, 2=half, 4=quarter, etc.
        ticks = (4 * self.ppq) // duration
        
        if dotted:
            ticks = int(ticks * 1.5)
        
        return ticks
    
    def _get_next_channel(self) -> int:
        """Get next available MIDI channel"""
        channel = self.channel_counter
        self.channel_counter += 1
        
        # Skip drum channel (9)
        if channel == GM_DRUM_CHANNEL:
            channel += 1
            self.channel_counter += 1
        
        if channel >= 16:
            raise ValueError("Too many instruments (max 15 non-percussion)")
        
        return channel
```

**Tasks**:
- [ ] Create MIDIGenerator class
- [ ] Implement instrument processing
- [ ] Implement note event generation
- [ ] Implement rest handling
- [ ] Implement chord generation
- [ ] Implement articulation state tracking
- [ ] Implement dynamic state tracking
- [ ] Implement slur generation (CC#68, note overlap)
- [ ] Implement slide generation (pitch bend, stepped, portamento)
- [ ] Implement percussion note generation
- [ ] Implement tempo/time signature meta-events
- [ ] Implement pan CC events
- [ ] Implement MIDI channel assignment
- [ ] Implement note-to-MIDI conversion
- [ ] Implement duration-to-ticks conversion
- [ ] Write MIDI generation unit tests
- [ ] Test with various MIDI analysis tools

---

## Phase 9: CLI & Integration (Days 14-15)

### 9.1 Command-Line Interface

**muslang/cli.py**:

```python
import argparse
import sys
from pathlib import Path
from muslang.parser import parse_muslang
from muslang.semantics import SemanticAnalyzer
from muslang.midi_gen import MIDIGenerator

def main():
    parser = argparse.ArgumentParser(
        description='Muslang: A music composition DSL compiler'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Compile command
    compile_parser = subparsers.add_parser('compile', help='Compile .mus to MIDI')
    compile_parser.add_argument('input', help='Input .mus file')
    compile_parser.add_argument('-o', '--output', help='Output MIDI file')
    compile_parser.add_argument('--ppq', type=int, default=480, 
                               help='MIDI resolution (PPQ)')
    compile_parser.add_argument('-v', '--verbose', action='store_true',
                               help='Verbose output')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check syntax/semantics')
    check_parser.add_argument('input', help='Input .mus file')
    check_parser.add_argument('-v', '--verbose', action='store_true')
    
    # Play command
    play_parser = subparsers.add_parser('play', help='Compile and play')
    play_parser.add_argument('input', help='Input .mus file')
    play_parser.add_argument('--player', default='fluidsynth',
                            choices=['fluidsynth', 'timidity'],
                            help='MIDI player')
    
    args = parser.parse_args()
    
    if args.command == 'compile':
        compile_file(args.input, args.output, args.ppq, args.verbose)
    elif args.command == 'check':
        check_file(args.input, args.verbose)
    elif args.command == 'play':
        play_file(args.input, args.player)
    else:
        parser.print_help()

def compile_file(input_path: str, output_path: str, ppq: int, verbose: bool):
    """Compile .mus file to MIDI"""
    try:
        # Read source
        with open(input_path, 'r') as f:
            source = f.read()
        
        if verbose:
            print(f"Parsing {input_path}...")
        
        # Parse
        ast = parse_muslang(source)
        
        if verbose:
            print("AST:")
            print(ast)
            print("\nAnalyzing...")
        
        # Semantic analysis
        analyzer = SemanticAnalyzer()
        ast = analyzer.analyze(ast)
        
        if analyzer.warnings:
            for warning in analyzer.warnings:
                print(f"Warning: {warning}", file=sys.stderr)
        
        if verbose:
            print("Generating MIDI...")
        
        # Generate MIDI
        if output_path is None:
            output_path = Path(input_path).stem + '.mid'
        
        generator = MIDIGenerator(ppq=ppq)
        generator.generate(ast, output_path)
        
        print(f"Successfully compiled to {output_path}")
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def check_file(input_path: str, verbose: bool):
    """Check .mus file for errors"""
    try:
        with open(input_path, 'r') as f:
            source = f.read()
        
        # Parse
        ast = parse_muslang(source)
        
        # Semantic analysis
        analyzer = SemanticAnalyzer()
        ast = analyzer.analyze(ast)
        
        if analyzer.warnings:
            for warning in analyzer.warnings:
                print(f"Warning: {warning}")
        
        print(f"✓ {input_path} is valid")
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def play_file(input_path: str, player: str):
    """Compile and play .mus file"""
    import tempfile
    import subprocess
    
    # Compile to temporary file
    with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
        temp_midi = f.name
    
    try:
        compile_file(input_path, temp_midi, 480, False)
        
        # Play with selected player
        if player == 'fluidsynth':
            subprocess.run(['fluidsynth', '-a', 'alsa', '-m', 'alsa_seq', 
                          '/usr/share/soundfonts/default.sf2', temp_midi])
        elif player == 'timidity':
            subprocess.run(['timidity', temp_midi])
    
    finally:
        Path(temp_midi).unlink(missing_ok=True)

if __name__ == '__main__':
    main()
```

**Tasks**:
- [ ] Create CLI with argparse
- [ ] Implement compile command
- [ ] Implement check command  
- [ ] Implement play command (with fluidsynth/timidity)
- [ ] Add verbose mode
- [ ] Add error handling and pretty printing
- [ ] Test CLI with examples
- [ ] Add entry point to pyproject.toml

---

## Phase 10: Testing (Days 15-17)

### 10.1 Test Suite Structure

**Test categories**:
1. **Parser tests**: Grammar coverage, error cases
2. **Semantic tests**: Validation, expansion, timing
3. **Articulation tests**: State tracking, MIDI mapping
4. **MIDI generation tests**: Correct MIDI events
5. **Integration tests**: End-to-end compilation
6. **Golden file tests**: Compare against reference MIDI files

**tests/test_parser.py**:
```python
import pytest
from muslang.parser import parse_muslang

def test_parse_simple_note():
    ast = parse_muslang("piano: c")
    assert len(ast.events) == 1
    assert ast.events[0].name == 'piano'

def test_parse_note_with_duration():
    ast = parse_muslang("piano: c4 d8 e2")
    notes = ast.events[0].events
    assert notes[0].duration == 4
    assert notes[1].duration == 8
    assert notes[2].duration == 2

def test_parse_accidentals():
    ast = parse_muslang("piano: c+ d- e")
    notes = ast.events[0].events
    assert notes[0].accidental == 'sharp'
    assert notes[1].accidental == 'flat'
    assert notes[2].accidental is None

# ... many more parser tests
```

**tests/test_integration.py**:
```python
import pytest
from muslang.parser import parse_muslang
from muslang.semantics import SemanticAnalyzer
from muslang.midi_gen import MIDIGenerator
import tempfile
import mido

def test_compile_basic_melody():
    source = """
    piano: o4 c4 d4 e4 f4 g2 g2
    """
    
    # Parse
    ast = parse_muslang(source)
    
    # Analyze
    analyzer = SemanticAnalyzer()
    ast = analyzer.analyze(ast)
    
    # Generate
    with tempfile.NamedTemporaryFile(suffix='.mid') as f:
        generator = MIDIGenerator()
        generator.generate(ast, f.name)
        
        # Verify MIDI file
        midi = mido.MidiFile(f.name)
        assert len(midi.tracks) > 0
        
        # Count note events
        note_ons = [msg for msg in midi.tracks[0] if msg.type == 'note_on']
        assert len(note_ons) == 7  # 7 notes

# ... many more integration tests
```

**Golden file tests**:
- Compile examples to MIDI
- Compare against reference MIDI files
- Verify note events, timing, velocities, CC messages

**Tasks**:
- [ ] Write parser unit tests (notes, rests, articulations, dynamics, etc.)
- [ ] Write semantic analyzer tests (validation, expansion, timing)
- [ ] Write articulation mapper tests (state tracking, velocity calculation)
- [ ] Write MIDI generator tests (event generation, channel assignment)
- [ ] Write integration tests (end-to-end compilation)
- [ ] Create golden file test suite
- [ ] Achieve >80% code coverage
- [ ] Test with various edge cases

---

## Phase 11: Documentation & Examples (Days 17-18)

### 11.1 Documentation

**docs/syntax_reference.md**: Complete language specification
**docs/articulation_guide.md**: Articulation system explanation
**docs/rhythm_guide.md**: Tuplets, grace notes, time signatures
**docs/ornaments_guide.md**: Trills, mordents, turns, tremolo
**docs/percussion_guide.md**: Drum notation

### 11.2 Example Compositions

**examples/basic_melody.mus**:
```muslang
# Simple melody demonstrating basic features
piano: (tempo! 120) (time 4 4) o4
  c4 d4 e4 f4 | g2 g2 | a4 a4 a4 a4 | g1 |
  f4 f4 f4 f4 | e2 e2 | d4 d4 d4 d4 | c1
```

**examples/articulation_showcase.mus**:
```muslang
# Showcase all articulation types
piano: (tempo! 100) o4
  # Natural (default)
  c4 d e f |
  
  # Staccato
  .staccato g a b o5 c |
  
  # Legato
  .legato d c o4 b a |
  
  # Reset to natural
  . g f e d |
  
  # Tenuto
  .tenuto c e g o5 c |
  
  # Slur
  {o4 g4 a b o5 c} |
  
  # Slides
  <o4 c4 o5 c> <.portamento o5 e o4 g> |
```

**examples/dynamics_demo.mus**:
```muslang
# Dynamic markings and transitions
piano: (tempo! 120) o4
  # Piano to forte
  .p c4 d e f .f g a b o5 c |
  
  # Crescendo
  .p .crescendo .f c4 d e f g a b o5 c |
  
  # Diminuendo
  .f .diminuendo .p o5 c4 o4 b a g f e d c |
  
  # Sforzando accents
  .sforzando c4 .sforzando e .sforzando g .sforzando o5 c |
```

**More examples**: rhythm_complex.mus, ornaments_demo.mus, drum_beat.mus, piano_voices.mus, orchestral.mus

**Tasks**:
- [ ] Write complete syntax reference
- [ ] Write articulation guide with examples
- [ ] Write rhythm guide
- [ ] Write ornaments guide
- [ ] Write percussion guide
- [ ] Create all example compositions
- [ ] Test all examples compile successfully
- [ ] Add comments explaining features

---

## Implementation Timeline

**Week 1** (Days 1-5):
- Phase 1: Project setup
- Phase 2: AST definitions
- Phase 3: Grammar definition (start)

**Week 2** (Days 6-10):
- Phase 3: Grammar definition (complete)
- Phase 4: Parser implementation
- Phase 5: Semantic analysis (start)

**Week 3** (Days 11-15):
- Phase 5: Semantic analysis (complete)
- Phase 6: Music theory support
- Phase 7: Articulation mapping
- Phase 8: MIDI generation (start)

**Week 4** (Days 16-20):
- Phase 8: MIDI generation (complete)
- Phase 9: CLI & integration
- Phase 10: Testing (start)

**Week 5** (Days 21-22):
- Phase 10: Testing (complete)
- Phase 11: Documentation & examples

**Total estimated time**: 22 days (4-5 weeks)

---

## Success Criteria

- [ ] All examples compile without errors
- [ ] Generated MIDI files play correctly
- [ ] Articulations audibly different (staccato vs legato)
- [ ] Dynamics audibly different (pp vs ff)
- [ ] Crescendo/diminuendo sound natural
- [ ] Slides sound smooth or stepped as specified
- [ ] Slurs group notes smoothly
- [ ] Ornaments expand correctly
- [ ] Tuplets have correct timing
- [ ] Grace notes are quick and before main note
- [ ] Percussion maps to correct drum sounds
- [ ] Multiple voices merge correctly
- [ ] Test suite passes (>80% coverage)
- [ ] Documentation complete and clear

---

## Next Steps

Ready to begin implementation! Start with Phase 1: Project Setup.
