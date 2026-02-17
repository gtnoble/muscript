# Muslang Syntax Reference

Complete language specification for the Muslang music composition DSL.

## Table of Contents

1. [Overview](#overview)
2. [Basic Structure](#basic-structure)
3. [Scientific Pitch Notation](#scientific-pitch-notation)
4. [Notes and Rests](#notes-and-rests)
5. [Durations](#durations)
6. [Accidentals](#accidentals)
7. [Chords](#chords)
8. [Articulations](#articulations)
9. [Dynamics](#dynamics)
10. [Ornaments](#ornaments)
11. [Rhythm Modifiers](#rhythm-modifiers)
12. [Grouping Constructs](#grouping-constructs)
13. [Directives](#directives)
14. [Structure and Voices](#structure-and-voices)
15. [Macro Preprocessing (m4)](#macro-preprocessing-m4)
16. [Percussion](#percussion)
17. [Comments](#comments)

---

## Overview

Muslang is a music composition DSL that uses:
- **Scientific pitch notation**: `c4/4` means C in octave 4, quarter note
- **Operator prefixes**: `:` for articulations, `@` for dynamics, `%` for ornaments
- **Left-to-right evaluation**: State changes apply to following notes
- **Alda-style philosophy**: Concise, readable, composable

---

## Basic Structure

A Muslang composition consists of **directives** (tempo, time signature, etc.) followed by one or more **instruments**, each containing **voices** with musical **events**:

```muslang
(tempo! 120);
(time 4 4);

instrument_name {
  V1: event1 event2 event3 ...;
  V2: event1 event2 event3 ...;
}
```

**Important**: 
- All notes, rests, chords, and other musical events must be contained within a voice (V1:, V2:, etc.)
- Directives like tempo and time signature must appear **before** instrument blocks (top-level)
- Instruments are enclosed in curly braces `{...}`
- Voice blocks terminate with a semicolon `;`
- `|` is used only between measures within a voice
- Instrument names use lowercase with optional underscores or hyphens

Example:
```muslang
(tempo! 120);
(time 4 4);

piano {
  V1: c4/4 d4/4 e4/4 f4/4;
}

violin {
  V1: g5/2 a5/2;
}
```

---

## Scientific Pitch Notation

Muslang uses **scientific pitch notation** where the octave is always specified with each note.

### Format
```
pitch [accidental] octave [/duration] [.] [~]
```

### Octaves
- `0-9`: Octave number (C4 = middle C)
- Always explicitly specified (no stateful octave tracking)

### Example
```muslang
c4    # C in octave 4 (middle C)
d5    # D in octave 5
a3    # A in octave 3
```

---

## Notes and Rests

### Notes
```muslang
piano {
  V1: c4 d4 e4 f4 g4 a4 b4 c5;
}
```

**Pitch letters**: `c`, `d`, `e`, `f`, `g`, `a`, `b` (lowercase)

### Rests
```muslang
piano {
  V1: c4/4 r/4 e4/4 r/4;
}
```

**Rest syntax**: `r` followed by optional duration

---

## Durations

Duration is specified after a slash `/`:

| Notation | Musical Value | Example |
|----------|---------------|---------|
| `/1`     | Whole note    | `c4/1`  |
| `/2`     | Half note     | `c4/2`  |
| `/4`     | Quarter note  | `c4/4`  |
| `/8`     | Eighth note   | `c4/8`  |
| `/16`    | 16th note     | `c4/16` |
| `/32`    | 32nd note     | `c4/32` |
| `/64`    | 64th note     | `c4/64` |

### Dotted Notes

Add a dot `.` after the duration to increase length by 50%:

```muslang
piano {
  V1: c4/4.  # Dotted quarter (1.5x quarter)
      d4/8.  # Dotted eighth (1.5x eighth)
}
```

### Default Duration

If duration is omitted, the last specified duration is used:

```muslang
piano {
  V1: c4/4 d4 e4 f4  # All are quarter notes
}
```

---

## Accidentals

### Sharp: `+` (after octave number)
```muslang
piano {
  V1: c4+/4  # C♯4 quarter note
      f5+/8  # F♯5 eighth note
}
```

### Flat: `-` (after octave number)
```muslang
piano {
  V1: b4-/4  # B♭4 quarter note
      e5-/8  # E♭5 eighth note
}
```

### Natural: (no accidental)
```muslang
piano {
  V1: c4/4   # C natural
}
```

---

## Chords

Multiple notes sounding simultaneously, separated by commas:

```muslang
# C major triad
piano {
  V1: c4/4,e4/4,g4/4;
}

# D minor seventh
piano {
  V1: d4/2,f4/2,a4/2,c5/2;
}
```

**Note**: All notes in a chord should have the same duration.

---

## Articulations

Articulations control **how notes are played**. Use `:` prefix.

### Types

| Articulation | Symbol      | Effect                          |
|--------------|-------------|---------------------------------|
| Natural      | `:natural`  | Natural/default (92% duration)  |
| Staccato     | `:staccato` | Short, detached (55% duration)  |
| Legato       | `:legato`   | Smooth, connected (100%)        |
| Tenuto       | `:tenuto`   | Full value, slightly emphasized |
| Marcato      | `:marcato`  | Strongly accented (90%)         |
| Reset        | `:reset`    | Pop articulation stack (undo)   |

### Syntax

```muslang
# Apply articulation to following notes
piano {
  V1: :staccato c4/4 d4/4 e4/4 f4/4;
}

# Change articulation mid-phrase
piano {
  V1: :staccato c4/4 d4/4 :legato e4/4 f4/4;
}

# Reset (undo last articulation change)
piano {
  V1: :staccato c4/4 d4/4 :reset e4/4 f4/4;
}
```

### Stack-Based Reset Behavior

Articulations use a **stack-based undo system**. Each articulation change pushes to the stack, and `:reset` pops the most recent change:

```muslang
piano {
  V1: c4/4 d4/4                    # Natural (system default)
      :staccato e4/4 f4/4 g4/4     # All staccato (pushed to stack)
      :legato a4/4 b4/4            # All legato (pushed to stack)
      :reset c5/4                  # Pops legato → back to staccato
      :reset d5/4                  # Pops staccato → back to natural
}
```

**Key points:**
- Each articulation change (`:staccato`, `:legato`, etc.) **pushes** to the stack
- `:reset` **pops** one level from the stack
- Composition and instrument-level defaults are pre-loaded on the stack
- The system default (natural) always remains at the bottom of the stack

---

## Dynamics

Dynamics control **loudness/volume**. Use `@` prefix.

### Absolute Levels

| Dynamic | Symbol | Velocity | Meaning        |
|---------|--------|----------|----------------|
| pp      | `@pp`  | 40       | pianissimo     |
| p       | `@p`   | 55       | piano          |
| mp      | `@mp`  | 70       | mezzo-piano    |
| mf      | `@mf`  | 85       | mezzo-forte    |
| f       | `@f`   | 100      | forte          |
| ff      | `@ff`  | 115      | fortissimo     |
| Reset    | `@reset` | (undo)   | Pop dynamic stack |

### Gradual Transitions

| Transition | Symbol         | Effect                  |
|------------|----------------|-------------------------|
| Crescendo  | `@crescendo`   | Gradually louder        |
| Diminuendo | `@diminuendo`  | Gradually softer        |
| Decresc    | `@decresc`     | Alias for diminuendo    |

### Accents (One-shot)

| Accent      | Symbol          | Effect                           |
|-------------|-----------------|----------------------------------|
| Sforzando   | `@sforzando`    | Sudden strong accent (+20 vel)   |
| Forte-piano | `@forte-piano`  | Strong then immediately soft     |

### Stack-Based Reset for Dynamics

Like articulations, dynamics also use a **stack-based undo system**. Use `@reset` to undo the last dynamic change:

```muslang
piano {
  V1: c4/4 d4/4                    # mf (system default)
      @p e4/4 f4/4                 # piano (pushed to stack)
      @f g4/4 a4/4                 # forte (pushed to stack)
      @reset b4/4 c5/4             # Pops forte → back to piano
      @reset d5/4                  # Pops piano → back to mf
}
```

**Independent stacks:**
- Articulation (`:reset`) and dynamic (`@reset`) stacks are **completely independent**
- `:reset` only undoes articulations
- `@reset` only undoes dynamics

### Examples

```muslang
# Absolute dynamics
piano {
  V1: @p c4/4 d4/4 @f e4/4 f4/4
}

# Crescendo
piano {
  V1: @p @crescendo c4/4 d4/4 e4/4 f4/4 @f g4/4
}

# Diminuendo
piano {
  V1: @f @diminuendo g4/4 f4/4 e4/4 d4/4 @p c4/4
}

# Accents
piano {
  V1: c4/4 @sforzando e4/4 g4/4 @sforzando c5/4
}
```

---

## Ornaments

Ornaments are decorative embellishments. Use `%` prefix.

### Types

| Ornament | Symbol    | Effect                                    |
|----------|-----------|-------------------------------------------|
| Trill    | `%trill`  | Rapid alternation with upper neighbor     |
| Mordent  | `%mordent`| Quick note-lower-note figure              |
| Turn     | `%turn`   | Upper-main-lower-main figure              |
| Tremolo  | `%tremolo`| Rapid repetition of same note             |

### Syntax

The ornament marker applies to the **immediately following note**:

```muslang
piano {
  V1: %trill c4/2       # Trill on C4 for half note duration
      %mordent d4/4     # Mordent on D4
      %turn e4/4        # Turn on E4
      %tremolo g4/1     # Tremolo on G4 for whole note
}
```

**Note**: Ornaments expand into multiple fast notes during compilation.

---

## Rhythm Modifiers

### Tuplets

Group notes to fit into a different time division. Use parentheses `()` and `:ratio`:

```muslang
# Triplet: 3 eighth notes in the space of 2
piano {
  V1: (c4/8 d4/8 e4/8):3
}

# Quintuplet: 5 notes in the space of 4
piano {
  V1: (c4/16 d4/16 e4/16 f4/16 g4/16):5
}

# Septuplet: 7 notes in the space of 4
piano {
  V1: (c4/16 d4/16 e4/16 f4/16 g4/16 a4/16 b4/16):7
}
```

### Grace Notes

Quick ornamental notes before the main note. Use `~` prefix:

```muslang
# Grace note before main note
piano {
  V1: ~c4/32 d4/4
}

# Multiple grace notes
piano {
  V1: ~c4/32 ~d4/32 e4/4
}
```

**Note**: Grace notes "steal" time from the following main note.

---

## Grouping Constructs

### Legato Phrasing

For smoothly connected notes, use the `:legato` articulation:

```muslang
# Slurred phrase via legato articulation
piano {
  V1: :legato c4/4 d4/4 e4/4 f4/4
}

# Mixed articulation phrasing
piano {
  V1: :legato c4/4 d4/4 :reset :staccato e4/4 f4/4
}
```

**MIDI implementation**: Sends CC#68 (legato), overlaps notes slightly while legato is active.

### Slides/Glissandi

Slide from one note to another. Use angle brackets `<>`:

```muslang
# Chromatic slide (default)
piano {
  V1: <c4/2 g4/2>
}

# Portamento (smooth pitch bend)
piano {
  V1: <portamento: c4/2 c5/2>
}

# Stepped (chromatic scale steps)
piano {
  V1: <stepped: c4/2 c5/2>
}
```

**Types**:
- **chromatic** (default): Pitch bend between notes
- **portamento**: Smooth pitch glide using CC
- **stepped**: Individual chromatic notes

---

## Directives

Directives set musical context. Use parentheses `()`:

### Tempo

```muslang
(tempo! 120);
piano {
  V1: c4/4 d4/4 e4/4;
}
```

**BPM**: Beats per minute (default: 120)

### Time Signature

```muslang
(time 3 4);
piano {
  V1: c4/4 d4/4 e4/4;
}
```

**Format**: `(time numerator denominator)`

Common signatures:
- `(time 4 4)` - 4/4 time (common time)
- `(time 3 4)` - 3/4 time (waltz)
- `(time 6 8)` - 6/8 time

### Key Signature

```muslang
(key g 'major);
piano {
  V1: g4/4 a4/4 b4/4 c5/4;
}
(key d 'minor);
piano {
  V1: d4/4 e4/4 f4/4 g4/4;
}
```

**Format**: `(key root 'mode)`
- **root**: `c`, `d`, `e`, `f`, `g`, `a`, `b` (with optional sharp `+` or flat `-`)
- **mode**: `'major` or `'minor`

**Examples with accidentals**:
```muslang
(key a- 'major);
piano {
  V1: e4-/4 f4/4 g4/4 a4-/4;  # A♭ major
}
(key f+ 'minor);
piano {
  V1: f4+/4 g4+/4 a4/4 b4/4;  # F♯ minor
}
```

**Effect**: Automatically applies scale accidentals to notes.

### Pan

```muslang
piano {
  (pan 64)
  V1: c4/4 d4/4  # Center
}
piano {
  (pan 0)
  V1: c4/4        # Far left
}
piano {
  (pan 127)
  V1: c4/4      # Far right
}
```

**Range**: 0-127 (0=left, 64=center, 127=right)

---

## Structure and Voices

### Multiple Instruments

```muslang
piano {
  V1: c4/4 d4/4 e4/4 f4/4;
}
violin {
  V1: g5/2 a5/2;
}
bass {
  V1: c2/1;
}
```

Each instrument gets its own MIDI track and channel.

### Voices (Polyphony)

Multiple melodic lines within one instrument. Use `V1:`, `V2:`, etc.:

```muslang
piano {
  V1: c4/4 d4/4 e4/4 f4/4;
  V2: e3/2 f3/2;
  V1: g4/4 a4/4 b4/4 c5/4;
}
```

**Important**: All notes must be in voices. Voices are required even for single-line melodies.

**Note**: Voices merge into a single MIDI track with interleaved events.

### Sequential Instrument Defaults

Instrument-level events can appear between voices and apply to subsequent voices:

```muslang
piano {
  @f;
  V1: c4/4 d4/4;
  @p;
  :staccato;
  V2: e4/4 f4/4;
}
```

### Voice Patterns with External Macros

For repeating polyphonic patterns, author with `m4` macros in a `.mus.m4` file and generate expanded `.mus` before compiling.

```m4
define(`BAR_V1', `V1: c4/4 d4/4 e4/4 f4/4;')
define(`BAR_V2', `V2: e3/2 f3/2;')

piano {
BAR_V1
BAR_V2
BAR_V1
BAR_V2
}
```

---

## Macro Preprocessing (m4)

Muslang base syntax does not include built-in variables or repeat blocks.
Use external `m4` preprocessing for reusable patterns.

### Workflow

1. Author source in `.mus.m4`.
2. Expand with `m4` to produce `.mus`.
3. Compile generated `.mus` with Muslang.

```bash
m4 score.mus.m4 > score.mus
python -m muslang.cli compile score.mus -o score.mid
```

### Example

```m4
define(`MOTIF', `c4/4 d4/4 e4/4 f4/4')

piano {
  V1: MOTIF MOTIF g4/2;
}
```

Generated `.mus`:

```muslang
piano {
  V1: c4/4 d4/4 e4/4 f4/4 c4/4 d4/4 e4/4 f4/4 g4/2;
}
```

### Recursive Repeat Helper

You can implement repeat behavior with recursive `m4` macros:

```m4
define(`REPEAT', `ifelse($1, `0', `', `$2`'REPEAT(decr($1), `$2')')')
define(`PATTERN', `kick/8 r/8 snare/8 r/8')

drums {
  V1: REPEAT(4, `PATTERN ');
}
```

Generated `.mus` (`V1` expanded 4 times):

```muslang
drums {
  V1: kick/8 r/8 snare/8 r/8 kick/8 r/8 snare/8 r/8 kick/8 r/8 snare/8 r/8 kick/8 r/8 snare/8 r/8;
}
```

---

## Percussion

Special drum notation for General MIDI percussion (channel 10).

### Drum Names

Common drums:
- `kick` - Bass drum
- `snare` - Snare drum
- `hat`, `hihat` - Closed hi-hat
- `openhat` - Open hi-hat
- `crash`, `crash2` - Crash cymbals
- `ride` - Ride cymbal
- `tom1`, `tom2`, `tom3`, `tom4` - Toms
- `rimshot` - Rimshot/side stick
- `clap` - Hand clap
- `cowbell` - Cowbell
- `tambourine` - Tambourine
- `splash` - Splash cymbal
- `china` - China cymbal

### Syntax

```muslang
# Percussion instrument
drums {
  V1: kick/4 snare/4 hat/8 hat/8 kick/4;
}

# Basic rock beat (expanded form)
drums {
  V1: kick/8 hat/8 snare/8 hat/8 kick/8 hat/8 snare/8 hat/8;
}
```

### Example Beat

```muslang
(tempo! 120);
drums {
  V1: kick/8 r/8 r/8 r/8 kick/8 r/8 r/8 r/8;
  V2: r/8 r/8 r/8 snare/8 r/8 r/8 r/8 snare/8;
  V3: hat/8 hat/8 hat/8 hat/8 hat/8 hat/8 hat/8 hat/8;
}
```

---

## Comments

Use `#` for single-line comments:

```muslang
# This is a comment
piano {
  V1: c4/4 d4/4;  # Another comment
}

# Comments can span the full line
# They are ignored by the parser
```

---

## Complete Example

```muslang
# Twinkle Twinkle Little Star
# Demonstrates multiple features

(tempo! 120);
(time 4 4);
(key c 'major);
piano {
  V1: # Main melody
      c4/4 c4/4 g4/4 g4/4 | a4/4 a4/4 g4/2 |
      f4/4 f4/4 e4/4 e4/4 | d4/4 d4/4 c4/2 |
  
      # With dynamics
      @mp g4/4 g4/4 f4/4 f4/4 | e4/4 e4/4 d4/2 |
      @mf g4/4 g4/4 f4/4 f4/4 | e4/4 e4/4 d4/2 |
  
      # With articulation
      :staccato c4/4 c4/4 g4/4 g4/4 |
      :legato a4/4 a4/4 g4/2 |
  
      # Repeat ending
      :reset f4/4 f4/4 e4/4 e4/4 | d4/4 d4/4 c4/2;
}
```

---

## Operator Prefix Summary

| Prefix | Purpose      | Examples                                    |
|--------|--------------|---------------------------------------------|
| `:`    | Articulation | `:natural`, `:staccato`, `:legato`, `:tenuto`, `:marcato`, `:reset` |
| `@`    | Dynamics     | `@p`, `@ff`, `@crescendo`, `@sforzando`     |
| `%`    | Ornaments    | `%trill`, `%mordent`, `%turn`, `%tremolo`   |
| `~`    | Grace notes  | `~c4/32`                                    |
| `/`    | Duration     | `/4`, `/8`, `/16`                           |
| `.`    | Dotted       | `/4.`, `/8.`                                |

---

## Syntax Quick Reference

```muslang
# Notes (must be in voices)
V1: c4 d4 e4;       # Pitches with octaves
    c4/4 d4/8       # With durations
    c4+ d4-         # With accidentals
    c4/4.           # Dotted

# Chords
V1: c4/4,e4/4,g4/4;

# Rests
V1: r/4 r/2;

# Articulations
:natural :staccato :legato :tenuto :marcato :reset

# Dynamics
@pp @p @mp @mf @f @ff
@crescendo @diminuendo @sforzando @forte-piano

# Ornaments
%trill %mordent %turn %tremolo

# Rhythm
(c4/8 d4/8 e4/8):3  # Tuplet
~c4/32 d4/4         # Grace note

# Grouping
<c4/2 g4/2>         # Slide

# Directives
(tempo! 120);
(time 4 4);
(key g 'major)
(pan 64)

# Structure
instrument_name {
  V1: events...;
}

# Macro preprocessing (m4, outside Muslang parser)
# define(`MELODY', `c4/4 d4/4')
# instrument { V1: MELODY MELODY; }

# Percussion
drums {
  V1: kick/4 snare/4 hat/8;
}

# Comments
# This is a comment
```

---

## Error Messages

The compiler provides helpful error messages:

```
Parse error: Expected duration, got 'x' at line 5, column 12
Semantic error: Octave out of range: 12 at line 8
Warning: Large slide interval: 26 semitones at line 15
```

---

## MIDI Output

The compiler generates **General MIDI (GM)** compatible files:
- **PPQ**: 480 ticks per quarter note (configurable)
- **Tracks**: One per instrument
- **Channels**: Automatically assigned (0-15, channel 9 reserved for drums)
- **Velocity**: Dynamics mapped to MIDI velocity (40-127)
- **CC messages**: Legato (68), pan (10), portamento (5, 65)
- **Meta-events**: Tempo, time signature

---

## Further Reading

- [Articulation Guide](articulation_guide.md) - Detailed articulation system
- [Rhythm Guide](rhythm_guide.md) - Tuplets, time signatures, complex rhythms
- [Ornaments Guide](ornaments_guide.md) - Trills, mordents, turns, tremolo
- [Percussion Guide](percussion_guide.md) - Complete drum notation reference

---

## Version

Muslang v0.1.0 - February 2026
