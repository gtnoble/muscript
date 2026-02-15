# Muslang Rhythm Guide

Complete guide to rhythm, timing, and time manipulation in Muslang.

## Table of Contents

1. [Introduction](#introduction)
2. [Basic Duration](#basic-duration)
3. [Dotted Notes](#dotted-notes)
4. [Tuplets](#tuplets)
5. [Grace Notes](#grace-notes)
6. [Time Signatures](#time-signatures)
7. [Tempo](#tempo)
8. [Ties](#ties)
9. [Rests](#rests)
10. [Complex Rhythms](#complex-rhythms)
11. [Polyrhythms](#polyrhythms)
12. [Musical Examples](#musical-examples)

---

## Introduction

Rhythm is the temporal organization of music. Muslang provides precise control over:

- **Duration**: How long notes last
- **Grouping**: Tuplets and irregular divisions
- **Timing**: Grace notes, ties, tempo changes
- **Meter**: Time signatures that define rhythmic structure

All timing in Muslang is based on **480 ticks per quarter note (PPQ)**, providing high precision for MIDI generation.

---

## Basic Duration

### Duration Syntax

Duration is specified after the slash `/`:

```muslang
note/duration
```

### Duration Values

| Value | Name         | Relative Length | Ticks (480 PPQ) |
|-------|--------------|-----------------|-----------------|
| `/1`  | Whole note   | 4 beats         | 1920            |
| `/2`  | Half note    | 2 beats         | 960             |
| `/4`  | Quarter note | 1 beat          | 480             |
| `/8`  | Eighth note  | 1/2 beat        | 240             |
| `/16` | 16th note    | 1/4 beat        | 120             |
| `/32` | 32nd note    | 1/8 beat        | 60              |
| `/64` | 64th note    | 1/16 beat       | 30              |

### Examples

```muslang
piano:
  V1: c4/1          # Whole note (4 beats)
      c4/2 c4/2     # Two half notes (2 + 2 = 4 beats)
      c4/4 c4/4 c4/4 c4/4  # Four quarter notes
      c4/8 c4/8 c4/8 c4/8 c4/8 c4/8 c4/8 c4/8  # Eight eighths
```

### Default Duration

If duration is omitted, the **previously specified duration** is used:

```muslang
piano:
  V1: c4/4 d4 e4 f4    # All quarter notes
      g4/8 a4 b4 c5    # All eighth notes
```

---

## Dotted Notes

### Syntax

Add a dot `.` after the duration to increase length by 50%:

```muslang
note/duration.
```

### Duration Calculation

```
dotted_duration = base_duration × 1.5
```

### Examples

| Notation | Base Duration | Dotted Duration | Ticks |
|----------|---------------|-----------------|-------|
| `/4.`    | 480 ticks     | 720 ticks       | 720   |
| `/8.`    | 240 ticks     | 360 ticks       | 360   |
| `/2.`    | 960 ticks     | 1440 ticks      | 1440  |

```muslang
piano:
  V1: c4/4.    # Dotted quarter (1.5 beats)
      d4/8     # Eighth note (0.5 beats)
      # Total: 2 beats
      
      e4/2.    # Dotted half (3 beats)
      f4/4     # Quarter (1 beat)
      # Total: 4 beats (one measure in 4/4)
```

### Common Rhythm Patterns

```muslang
# Dotted eighth + sixteenth (swing feel)
piano:
  V1: c4/8. d4/16 e4/8. f4/16

# Dotted quarter + eighth (common in 6/8 time)
piano: (time 6 8)
  V1: c4/4. d4/8 e4/4. f4/8
```

---

## Tuplets

Tuplets fit a group of notes into a different time division.

### Syntax

```muslang
(note1 note2 ... noteN):ratio
```

- **Parentheses** `()` group the notes
- **Colon-ratio** `:N` specifies the tuplet type
- **Ratio**: How many notes to fit (3 = triplet, 5 = quintuplet, etc.)

### Common Tuplets

#### Triplets (3 notes in space of 2)

```muslang
# Triplet of eighth notes (fits into one quarter note)
piano:
  V1: (c4/8 d4/8 e4/8):3
```

**Timing**:
- 3 eighth notes normally = 720 ticks
- Triplet compresses to = 480 ticks (one quarter)
- Each note = 160 ticks

```muslang
# Triplet quarter notes (fits into one half note)
piano:
  V1: (c4/4 d4/4 e4/4):3
```

#### Quintuplets (5 notes in space of 4)

```muslang
# 5 sixteenth notes in space of 4
piano:
  V1: (c4/16 d4/16 e4/16 f4/16 g4/16):5
```

#### Septuplets (7 notes in space of 4)

```muslang
# 7 notes in space of 4
piano:
  V1: (c4/16 d4/16 e4/16 f4/16 g4/16 a4/16 b4/16):7
```

### Tuplet Calculation

```
actual_duration = (sum of note durations) × (ratio / note_count)
```

Example for triplet:
```
(c4/8 d4/8 e4/8):3
- Sum: 240 + 240 + 240 = 720 ticks
- Ratio: 3 (triplet)
- Note count: 3 notes
- Actual: 720 × (3/3) = 480 ticks
- But wait, we want 2:3 ratio (2 beats of time, 3 notes)
- Actually: 720 × (2/3) = 480 ticks
```

### Mixed Tuplets

```muslang
piano:
  V1: (c4/8 d4/8 e4/8):3  # Triplet
      f4/4                 # Regular quarter
      (g4/16 a4/16 b4/16 c5/16 d5/16):5  # Quintuplet
```

### Nested Tuplets

```muslang
# Tuplet inside another tuplet
piano:
  V1: (
        c4/8 
        (d4/16 e4/16 f4/16):3  # Triplet of 16ths
        g4/8
      ):3  # All in a triplet
```

---

## Grace Notes

Grace notes are quick ornamental notes that "steal" time from the following main note.

### Syntax

```muslang
~grace_note main_note
```

Use tilde `~` before the grace note.

### Examples

```muslang
# Single grace note
piano:
  V1: ~c4/32 d4/4

# Multiple grace notes
piano:
  V1: ~c4/32 ~d4/32 e4/4

# Grace note before chord
piano:
  V1: ~g4/32 c4/4,e4/4,g4/4
```

### Timing

Grace notes occupy **5% of a quarter note** (24 ticks at 480 PPQ), regardless of their written duration.

```
grace_duration = 480 × 0.05 = 24 ticks
main_note starts: grace_note_start + 24 ticks
```

The grace note doesn't add to total duration - it "steals" from the preceding space or from the main note's attack.

### Acciaccatura vs Appoggiatura

Muslang treats all grace notes as **acciaccaturas** (crushed, very quick). Future versions may support appoggiaturas (slower, on-beat grace notes).

---

## Time Signatures

Time signatures define the rhythmic meter and beat grouping.

### Syntax

```muslang
(time numerator denominator)
```

### Common Time Signatures

| Signature   | Syntax        | Beats per Measure | Beat Unit    |
|-------------|---------------|-------------------|--------------|
| 4/4         | `(time 4 4)`  | 4                 | Quarter note |
| 3/4         | `(time 3 4)`  | 3                 | Quarter note |
| 2/4         | `(time 2 4)`  | 2                 | Quarter note |
| 6/8         | `(time 6 8)`  | 6                 | Eighth note  |
| 12/8        | `(time 12 8)` | 12                | Eighth note  |
| 5/4         | `(time 5 4)`  | 5                 | Quarter note |
| 7/8         | `(time 7 8)`  | 7                 | Eighth note  |

### Examples

#### 4/4 (Common Time)

```muslang
piano: (time 4 4)
  V1: c4/4 d4/4 e4/4 f4/4 |  # 4 quarter notes = 1 measure
      g4/2 g4/2 |             # 2 half notes = 1 measure
      c4/1 |                  # 1 whole note = 1 measure
```

#### 3/4 (Waltz Time)

```muslang
piano: (time 3 4)
  V1: c4/4 e4/4 g4/4 |  # 3 quarter notes = 1 measure
      c5/2 g4/4 |       # Dotted half is too long!
      c5/4. g4/8 g4/8 | # This works
```

#### 6/8 (Compound Meter)

```muslang
piano: (time 6 8)
  V1: c4/8 d4/8 e4/8 f4/8 g4/8 a4/8 |  # 6 eighth notes
      b4/4. g4/4. |                    # 2 dotted quarters (2 beats)
```

#### 5/4 (Irregular Meter)

```muslang
piano: (time 5 4)
  V1: c4/4 d4/4 e4/4 f4/4 g4/4 |  # 5 quarter notes
      a4/2. g4/2 |               # Dotted half + half
```

### Changing Time Signatures

```muslang
piano:
  (time 4 4)
  V1: c4/4 d4/4 e4/4 f4/4 |
  
  (time 3 4)
  V1: g4/4 a4/4 b4/4 |
  
  (time 6 8)
  V1: c5/4. b4/4. |
```

---

## Tempo

Tempo controls the speed of playback in **beats per minute (BPM)**.

### Syntax

```muslang
(tempo! bpm)
```

### Examples

```muslang
# Slow tempo (60 BPM = 1 beat per second)
piano: (tempo! 60)
  V1: c4/4 d4/4 e4/4 f4/4

# Moderate tempo
piano: (tempo! 120)  # Default
  V1: c4/4 d4/4 e4/4 f4/4

# Fast tempo
piano: (tempo! 180)
  V1: c4/4 d4/4 e4/4 f4/4
```

### Common Tempo Markings

| Marking    | BPM Range | Example      |
|------------|-----------|--------------|
| Largo      | 40-60     | `(tempo! 50)`  |
| Adagio     | 60-80     | `(tempo! 70)`  |
| Andante    | 80-100    | `(tempo! 90)`  |
| Moderato   | 100-120   | `(tempo! 110)` |
| Allegro    | 120-160   | `(tempo! 140)` |
| Presto     | 160-200   | `(tempo! 180)` |

### Tempo Changes

```muslang
piano:
  (tempo! 120)
  V1: c4/4 d4/4 e4/4 f4/4 |
  
  (tempo! 90)  # Slow down
  V1: g4/4 a4/4 b4/4 c5/4 |
  
  (tempo! 160)  # Speed up
  V1: c5/8 b4/8 a4/8 g4/8 f4/8 e4/8 d4/8 c4/8 |
```

---

## Ties

Ties connect two notes of the same pitch, creating a single sustained note.

### Syntax

```muslang
note1~ note2
```

Add tilde `~` **after** the first note.

### Examples

```muslang
# Tie two quarter notes (= half note)
piano:
  V1: c4/4~ c4/4

# Tie across measures
piano: (time 4 4)
  V1: c4/2 d4/4 e4/4~ |
      e4/4 f4/4 g4/2 |

# Multiple ties
piano:
  V1: c4/4~ c4/4~ c4/4~ c4/4  # = whole note
```

### Use Cases

#### Sustain Across Bar Lines

```muslang
piano: (time 4 4)
  V1: c4/4 d4/4 e4/4 f4/4~ |
      f4/4 e4/4 d4/4 c4/4 |
```

#### Non-Standard Durations

```muslang
# 5 eighths = dotted quarter + quarter tied
piano:
  V1: c4/8~ c4/4~ c4/8

# 7 sixteenths
piano:
  V1: c4/16~ c4/8~ c4/4
```

### MIDI Implementation

Tied notes generate a single MIDI note-on/off pair with combined duration:
```
c4/4~ c4/4  →  MIDI: note_on(C4, 960 ticks)
```

---

## Rests

Rests are periods of silence.

### Syntax

```muslang
r/duration
```

### Examples

```muslang
# Quarter rest
piano:
  V1: c4/4 r/4 e4/4 r/4

# Multiple rest durations
piano:
  V1: c4/4 r/8 r/8 e4/4 r/2

# Dotted rests
piano:
  V1: c4/4 r/4. d4/8
```

### Rest Equivalents

Rests can be combined like notes:
```muslang
# Whole rest = 4 quarter rests
piano:
  V1: r/1  # Same as...
piano:
  V1: r/4 r/4 r/4 r/4
```

---

## Complex Rhythms

### Syncopation

Notes emphasized on weak beats or off-beats:

```muslang
piano: (tempo! 120) (time 4 4)
  V1: r/8 c4/8 r/8 e4/8 r/8 g4/8 r/8 c5/8 |
      r/8 c5/8 r/8 g4/8 r/8 e4/8 r/8 c4/8 |
```

### Hemiola

Grouping that conflicts with the time signature:

```muslang
# 6/8 time played with 3/4 feel
piano: (time 6 8)
  V1: c4/4 d4/4 e4/4 |  # Feels like 3/4
      f4/8 f4/8 f4/8 g4/8 g4/8 g4/8 |  # Back to 6/8 feel
```

### Cross-Rhythm

```muslang
# 3 against 2
piano:
  V1: (c4/8 d4/8 e4/8):3  # 3 notes
  V2: f3/8 g3/8           # 2 notes
```

### Swing Rhythm

Unequal eighth notes (long-short pattern):

```muslang
# Simulated swing using dotted 8th + 16th
piano: (tempo! 150)
  V1: c4/8. d4/16 e4/8. f4/16 g4/8. a4/16 b4/4 |
```

---

## Polyrhythms

Multiple rhythmic patterns played simultaneously.

### 3 Against 2

```muslang
piano:
  V1: (c5/4 d5/4 e5/4):3    # 3 notes in 2 beats
  V2: c3/4 g3/4              # 2 notes in 2 beats
```

### 5 Against 4

```muslang
piano:
  V1: (c5/16 d5/16 e5/16 f5/16 g5/16):5  # 5 in 4
  V2: c3/16 e3/16 g3/16 c4/16           # 4 notes
```

### Polymetric (Different Time Signatures)

Muslang doesn't support different time signatures simultaneously, but you can simulate:

```muslang
# Simulate 3/4 against 6/8
piano:
  V1: c5/4 d5/4 e5/4 c5/4 d5/4 e5/4  # 3/4 feel (2 measures)
  V2: c3/8 c3/8 c3/8 e3/8 e3/8 e3/8 g3/8 g3/8 g3/8 c4/8 c4/8 c4/8  # 6/8 (2 measures)
```

---

## Musical Examples

### Example 1: Simple Rhythm

```muslang
# Basic melody with varied durations
piano: (tempo! 120) (time 4 4)
  V1: c4/4 d4/4 e4/4 f4/4 |
      g4/2 g4/2 |
      a4/4 a4/4 a4/4 a4/4 |
      g4/1 |
```

### Example 2: Sixteenth Note Patterns

```muslang
# Fast sixteenth note runs
piano: (tempo! 120)
  V1: c4/16 d4/16 e4/16 f4/16 g4/16 a4/16 b4/16 c5/16 |
      c5/16 b4/16 a4/16 g4/16 f4/16 e4/16 d4/16 c4/16 |
```

### Example 3: Triplet Groove

```muslang
# Triplet-based rhythm
piano: (tempo! 100)
  V1: c4/8 (d4/8 e4/8 f4/8):3 g4/8 (a4/8 b4/8 c5/8):3 |
      c5/4 (b4/8 a4/8 g4/8):3 f4/4 r/4 |
```

### Example 4: Grace Note Ornaments

```muslang
# Melody with grace notes
piano: (tempo! 90)
  V1: ~c4/32 d4/4 ~e4/32 f4/4 |
      ~g4/32 ~a4/32 b4/2 |
      ~c5/32 c5/4. ~b4/32 b4/8 |
      c5/1 |
```

### Example 5: Complex Time Signature (5/4)

```muslang
# Famous 5/4 rhythm (Take Five style)
piano: (tempo! 170) (time 5 4)
  V1: c4/4 c4/8 d4/8 e4-/8 f4/8 g4/4 g4/4 |
      f4/4 f4/8 g4/8 a4-/8 b4-/8 c5/4 c5/4 |
```

### Example 6: Waltz (3/4 with Grace Notes)

```muslang
# Elegant waltz with embellishments
piano: (tempo! 160) (time 3 4)
  V1: @mp ~b3/32 c4/4 e4/4 g4/4 |
      c5/4. b4/8 a4/8 g4/8 |
      ~f4/32 f4/4 a4/4 c5/4 |
      f5/2 e5/4 |
```

### Example 7: Syncopated Rhythm

```muslang
# Off-beat emphasis
piano: (tempo! 120) (time 4 4)
  V1: r/8 c4/8 r/8 e4/4 g4/8 r/4 |
      r/8 c5/8 r/4 g4/8 e4/8 c4/4 |
```

### Example 8: Mixed Tuplets

```muslang
# Various tuplet types
piano: (tempo! 100)
  V1: (c4/8 d4/8 e4/8):3 f4/8 |  # Triplet
      (g4/16 a4/16 b4/16 c5/16 d5/16):5 e5/8 |  # Quintuplet
      (f5/16 e5/16 d5/16 c5/16 b4/16 a4/16 g4/16):7 f4/8 |  # Septuplet
```

### Example 9: Compound Meter (6/8)

```muslang
# Flowing 6/8 melody
piano: (tempo! 80) (time 6 8)
  V1: c4/8 e4/8 g4/8 c5/4. |
      b4/8 g4/8 e4/8 d4/4. |
      c4/8 d4/8 e4/8 f4/8 g4/8 a4/8 |
      g4/4. e4/4. |
```

### Example 10: Polyrhythmic Pattern

```muslang
# 3 against 2
piano: (tempo! 100)
  V1: [(c5/4 d5/4 e5/4):3] * 4
  V2: [c3/4 g3/4] * 6
```

---

## Best Practices

### 1. Align with Time Signature

Ensure measures add up correctly:

```muslang
# Good - 4/4 time, 4 beats per measure
piano: (time 4 4)
  V1: c4/4 d4/4 e4/4 f4/4 |  # ✓ 4 beats

# Bad - doesn't add up
piano: (time 4 4)
  V1: c4/4 d4/4 e4/4 |  # ✗ Only 3 beats
```

### 2. Use Bar Lines for Clarity

Bar lines `|` are visual only but help readability:

```muslang
# Clear measure boundaries
piano: (time 4 4)
  V1: c4/4 d4/4 e4/4 f4/4 |
      g4/4 a4/4 b4/4 c5/4 |
```

### 3. Tuplets for Odd Divisions

Use tuplets instead of calculating complex tick values:

```muslang
# Good - clear triplet
piano:
  V1: (c4/8 d4/8 e4/8):3

# Bad - trying to manually time triplets
# (Not easily possible in Muslang)
```

### 4. Grace Notes for Quick Ornaments

Grace notes are for quick decorations only:

```muslang
# Good - quick grace
piano:
  V1: ~c4/32 d4/4

# Questionable - if you want a slow grace, use normal notes
piano:
  V1: c4/16 d4/4
```

---

## Troubleshooting

### Problem: Rhythm sounds off

**Check**: Ensure measures add up correctly with time signature
```muslang
piano: (time 4 4)
  V1: c4/4 d4/4 e4/4 f4/4 |  # ✓ 4 beats total
```

### Problem: Tuplet doesn't sound right

**Check**: Ratio should match note count typically
```muslang
# 3 notes = use :3
piano:
  V1: (c4/8 d4/8 e4/8):3  # ✓

# Not typically:
piano:
  V1: (c4/8 d4/8 e4/8):5  # ✗ Weird timing
```

### Problem: Grace notes too loud

**Solution**: Grace notes inherit dynamics - set to softer before grace
```muslang
piano:
  V1: @mp ~c4/32 @f d4/4  # Soft grace, loud main note
```

---

## See Also

- [Syntax Reference](syntax_reference.md) - Complete language specification
- [Articulation Guide](articulation_guide.md) - Articulation and dynamics
- [Ornaments Guide](ornaments_guide.md) - Trills, mordents, turns
- [Examples](../examples/) - Complete musical examples

---

## Version

Muslang v0.1.0 - February 2026
