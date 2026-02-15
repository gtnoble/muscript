# Muslang Percussion Guide

Complete guide to drum and percussion notation in Muslang.

## Table of Contents

1. [Introduction](#introduction)
2. [Percussion Basics](#percussion-basics)
3. [Drum Kit Mapping](#drum-kit-mapping)
4. [Common Drum Patterns](#common-drum-patterns)
5. [Percussion Techniques](#percussion-techniques)
6. [Dynamics and Articulation](#dynamics-and-articulation)
7. [Musical Examples](#musical-examples)
8. [Complete Drum Reference](#complete-drum-reference)

---

## Introduction

Muslang provides comprehensive percussion support using **General MIDI drum mapping (Channel 10)**. Instead of pitch notation, drums use **descriptive names** that map to standard drum sounds.

### Key Features

- **Name-based notation**: `kick`, `snare`, `hat` instead of pitches
- **General MIDI standard**: Compatible with all GM synthesizers
- **Duration support**: Drums can have durations like melodic notes
- **Full expression**: Dynamics, articulation work the same way
- **Easy patterns**: Simple notation for complex rhythms

---

## Percussion Basics

### Syntax

```muslang
drums: drum_name/duration ...
```

or

```muslang
percussion: drum_name/duration ...
```

### Simple Example

```muslang
drums:
  V1: kick/4 snare/4 hat/8 hat/8
```

### Duration

Drums use the same duration syntax as melodic notes:

```muslang
drums:
  V1: kick/4      # Quarter note kick
      snare/8     # Eighth note snare
      hat/16      # Sixteenth note hi-hat
```

### Multiple Drums Simultaneously

To play drums at the same time, use multiple voices (not chords - drums don't form chords):

```muslang
drums:
  V1: kick/4 r/4 kick/4 r/4
  V2: r/4 snare/4 r/4 snare/4
  V3: hat/8 hat/8 hat/8 hat/8 hat/8 hat/8 hat/8 hat/8
```

---

## Drum Kit Mapping

### Core Drum Kit

The essential elements of a standard drum kit:

| Name      | Sound           | MIDI Note | Use                    |
|-----------|-----------------|-----------|------------------------|
| `kick`    | Bass Drum       | 36        | Low, powerful beat     |
| `snare`   | Snare Drum      | 38        | Backbeat, main rhythm  |
| `hat`     | Closed Hi-Hat   | 42        | Fast rhythm, timekeeping |
| `hihat`   | Closed Hi-Hat   | 42        | Alias for `hat`        |
| `openhat` | Open Hi-Hat     | 46        | Accented hi-hat        |

### Toms

| Name   | Sound          | MIDI Note | Pitch  |
|--------|----------------|-----------|--------|
| `tom1` | High Tom       | 48        | High   |
| `tom2` | Mid Tom        | 45        | Mid    |
| `tom3` | Floor Tom High | 43        | Low    |
| `tom4` | Floor Tom Low  | 41        | Lowest |

### Cymbals

| Name     | Sound         | MIDI Note | Use                    |
|----------|---------------|-----------|------------------------|
| `crash`  | Crash Cymbal  | 49        | Accents, transitions   |
| `crash2` | Crash 2       | 57        | Secondary crash        |
| `ride`   | Ride Cymbal   | 51        | Alternative to hi-hat  |
| `splash` | Splash Cymbal | 55        | Quick accent           |
| `china`  | China Cymbal  | 52        | Exotic, trashy sound   |

### Auxiliary Percussion

| Name         | Sound         | MIDI Note | Use                 |
|--------------|---------------|-----------|---------------------|
| `rimshot`    | Side Stick    | 37        | Rim click, accent   |
| `clap`       | Hand Clap     | 39        | Electronic, accent  |
| `cowbell`    | Cowbell       | 56        | More cowbell!       |
| `tambourine` | Tambourine    | 54        | Jingle, shake       |

---

## Common Drum Patterns

### Basic Rock Beat

The foundation of rock music - kick on 1 and 3, snare on 2 and 4, hi-hat eighths:

```muslang
drums: (tempo! 120)
  V1: kick/8 r/8 r/8 r/8 kick/8 r/8 r/8 r/8
  V2: r/8 r/8 r/8 snare/8 r/8 r/8 r/8 snare/8
  V3: hat/8 hat/8 hat/8 hat/8 hat/8 hat/8 hat/8 hat/8
```

Or more compactly with voices inside a repeat block:

```muslang
drums: (tempo! 120)
  [
    V1: kick/8 r/8 r/8 r/8 kick/8 r/8 r/8 r/8
    V2: r/8 r/8 r/8 snare/8 r/8 r/8 r/8 snare/8
    V3: hat/8 hat/8 hat/8 hat/8 hat/8 hat/8 hat/8 hat/8
  ] * 4
```

**Note**: This syntax allows you to define polyphonic patterns (multiple voices playing simultaneously) and repeat them as a unit.

### Simple Backbeat

Classic 4/4 with kick and snare:

```muslang
drums: (time 4 4) (tempo! 120)
  [
    V1: kick/4 kick/4 kick/4 kick/4
    V2: r/4 snare/4 r/4 snare/4
  ] * 4
```

### Disco Beat

Famous four-on-the-floor with hi-hat eighths:

```muslang
drums: (tempo! 120)
  [
    V1: kick/4 kick/4 kick/4 kick/4
    V2: r/4 snare/4 r/4 snare/4
    V3: hat/8 hat/8 hat/8 hat/8 hat/8 hat/8 hat/8 hat/8
  ] * 4
```

### Funk Pattern

Syncopated 16th notes with ghost notes:

```muslang
drums: (tempo! 110)
  V1: kick/16 r/16 kick/16 r/16 r/16 r/16 kick/16 r/16 kick/16 r/16 r/16 r/16 r/16 r/16 kick/16 r/16
  V2: r/16 r/16 r/16 r/16 @p snare/16 @mf snare/16 r/16 r/16 r/16 r/16 r/16 r/16 snare/16 r/16 r/16 @p snare/16
  V3: hat/16 hat/16 hat/16 hat/16 hat/16 hat/16 hat/16 hat/16 hat/16 hat/16 hat/16 hat/16 hat/16 hat/16 hat/16 hat/16
```

### Jazz Swing

Ride cymbal pattern with cross-stick:

```muslang
drums: (tempo! 140)
  V1: kick/4. kick/8 kick/4 kick/4
  V2: r/4 rimshot/4 r/4 rimshot/4
  V3: ride/8. ride/16 ride/8 ride/8. ride/16 ride/8 ride/8. ride/16 ride/8 ride/8. ride/16 ride/8
```

### Latin Pattern

Clave-based rhythm:

```muslang
drums: (tempo! 100)
  V1: kick/8 r/8 kick/8 r/8 kick/8 r/8 r/8 r/8
  V2: r/8 r/8 snare/8 r/8 r/8 snare/8 r/8 snare/8
  V3: hat/8 hat/8 hat/8 hat/8 hat/8 hat/8 hat/8 hat/8
  V4: cowbell/4 r/8 cowbell/8 r/4 cowbell/8 r/8
```

### Drum Fill

Tom-based fill leading to crash:

```muslang
drums:
  tom1/16 tom1/16 tom2/16 tom2/16 tom3/16 tom3/16 tom4/16 tom4/16 crash/2
```

---

## Percussion Techniques

### Ghost Notes

Very quiet snare hits (common in funk):

```muslang
drums:
  @mf snare/16 @pp snare/16 @p snare/16 @mf snare/16
```

### Flams

Two very close hits (grace note + main note):

```muslang
drums:
  ~snare/32 snare/4
```

### Rim Click vs Full Snare

Use `rimshot` for side stick, `snare` for full hit:

```muslang
drums:
  kick/4 rimshot/4 kick/4 snare/4
```

### Open/Closed Hi-Hat

Alternate between `hat` (closed) and `openhat` (open):

```muslang
drums:
  hat/8 hat/8 openhat/8 hat/8 hat/8 hat/8 openhat/8 hat/8
```

### Cymbal Crashes

Use crashes for emphasis:

```muslang
drums:
  # Build-up
  tom1/8 tom1/8 tom2/8 tom2/8 tom3/8 tom3/8 tom4/8 tom4/8
  # Crash!
  crash/2 kick/4 snare/4
```

### Rolls

Fast repeated hits (snare roll):

```muslang
drums:
  # Snare roll (32nd notes)
  [snare/32] * 16 crash/2
```

---

## Dynamics and Articulation

### Dynamics on Drums

Drums respond to dynamics like melodic instruments:

```muslang
drums:
  # Soft kick
  @p kick/4 kick/4
  
  # Loud snare
  @ff snare/4 snare/4
  
  # Crescendo on hi-hat
  @pp @crescendo hat/8 hat/8 hat/8 hat/8 hat/8 hat/8 @f hat/8 hat/8
```

### Articulation Effects

```muslang
drums:
  # Staccato hi-hat (short, tight)
  :staccato hat/8 hat/8 hat/8 hat/8
  
  # Tenuto kick (full sustained)
  :tenuto kick/4 kick/4
```

### Accents

Use sforzando for accented hits:

```muslang
drums:
  hat/8 hat/8 @sforzando hat/8 hat/8 hat/8 hat/8 @sforzando hat/8 hat/8
```

---

## Musical Examples

### Example 1: Basic Rock Groove

```muslang
drums: (tempo! 120) (time 4 4)
  [
    V1: kick/8 r/8 r/8 r/8 kick/8 r/8 r/8 r/8
    V2: r/8 r/8 r/8 snare/8 r/8 r/8 r/8 snare/8
    V3: hat/8 hat/8 hat/8 hat/8 hat/8 hat/8 hat/8 hat/8
  ] * 8
```

### Example 2: Buildup with Dynamics

```muslang
drums: (tempo! 130)
  # Start quiet
  @pp
  [kick/4 snare/4] * 4
  
  # Build up
  @mp @crescendo
  [kick/4 snare/4] * 4
  
  # Climax
  @ff
  kick/4 snare/4 kick/4 crash/4
```

### Example 3: Complex 16th Pattern

```muslang
drums: (tempo! 110)
  V1: kick/16 r/16 kick/16 r/16 r/16 r/16 kick/16 r/16 
      kick/16 r/16 r/16 r/16 r/16 kick/16 r/16 r/16
  V2: r/16 r/16 r/16 r/16 snare/16 r/16 @p snare/16 r/16 
      r/16 r/16 r/16 r/16 @mf snare/16 r/16 @p snare/16 @mf snare/16
  V3: [hat/16] * 16
```

### Example 4: Drum Fill with Toms

```muslang
drums: (tempo! 140)
  # Regular beat
  [
    V1: kick/8 r/8 r/8 r/8 kick/8 r/8 r/8 r/8
    V2: r/8 r/8 r/8 snare/8 r/8 r/8 r/8 snare/8
    V3: hat/8 hat/8 hat/8 hat/8 hat/8 hat/8 hat/8 hat/8
  ] * 3
  
  # Fill
  @f tom1/8 tom1/8 tom2/8 tom2/8 tom3/8 tom3/8 tom4/8 tom4/8
  crash/4 kick/4 snare/4 kick/4
```

### Example 5: Funky Ghost Notes

```muslang
drums: (tempo! 100)
  V1: kick/16 r/16 kick/16 r/16 r/16 r/16 kick/16 r/16 
      kick/16 r/16 r/16 r/16 kick/16 r/16 r/16 r/16
  V2: r/16 r/16 r/16 r/16 @f snare/16 @pp snare/16 @p snare/16 @pp snare/16 
      r/16 r/16 r/16 r/16 @f snare/16 @pp snare/16 @p snare/16 @f snare/16
  V3: :staccato [hat/16] * 16
```

### Example 6: Jazz Ride Pattern

```muslang
drums: (tempo! 160)
  V1: kick/4. r/8 r/2
  V2: r/4 rimshot/4 r/4 rimshot/4
  V3: ride/8. ride/16 ride/8 ride/8. ride/16 ride/8 
      ride/8. ride/16 ride/8 ride/8. ride/16 ride/8
```

### Example 7: Latin Percussion

```muslang
drums: (tempo! 110)
  V1: kick/8 r/8 kick/8 kick/8 r/8 r/8 kick/8 r/8
  V2: r/8 r/8 snare/8 r/8 r/8 snare/8 r/8 snare/8
  V3: hat/8 hat/8 hat/8 hat/8 hat/8 hat/8 hat/8 hat/8
  V4: cowbell/4 r/8 cowbell/8 r/4 cowbell/8 cowbell/8
  V5: [tambourine/16 r/16] * 8
```

### Example 8: Metal Double Bass

```muslang
drums: (tempo! 180)
  V1: [kick/16 kick/16] * 8  # Fast double kick
  V2: r/8 r/8 r/8 snare/8 r/8 r/8 r/8 snare/8
  V3: [hat/16] * 16
  V4: r/2 r/4 crash/4  # Occasional crash
```

### Example 9: Breakbeat Pattern

```muslang
drums: (tempo! 140)
  V1: kick/16 r/16 r/16 kick/16 r/16 r/16 r/16 r/16 
      kick/16 r/16 r/16 r/16 kick/16 r/16 r/16 r/16
  V2: r/16 r/16 r/16 r/16 snare/16 r/16 snare/16 r/16 
      r/16 snare/16 r/16 r/16 snare/16 r/16 snare/16 snare/16
  V3: hat/8 hat/8 openhat/8 hat/8 hat/8 hat/8 openhat/8 hat/8
```

### Example 10: Progressive Time (7/8)

```muslang
drums: (tempo! 130) (time 7 8)
  V1: kick/8 r/8 kick/8 r/8 kick/8 r/8 r/8
  V2: r/8 r/8 snare/8 r/8 r/8 snare/8 r/8
  V3: hat/8 hat/8 hat/8 hat/8 hat/8 hat/8 hat/8
```

---

## Complete Drum Reference

### Full General MIDI Drum Map

| Drum Name    | Sound Description        | MIDI Note | Category   |
|--------------|--------------------------|-----------|------------|
| `kick`       | Acoustic Bass Drum       | 36        | Kick       |
| `kick2`      | Bass Drum 1              | 35        | Kick       |
| `snare`      | Acoustic Snare           | 38        | Snare      |
| `snare2`     | Electric Snare           | 40        | Snare      |
| `rimshot`    | Side Stick/Rimshot       | 37        | Snare      |
| `hat`        | Closed Hi-Hat            | 42        | Hi-Hat     |
| `hihat`      | Closed Hi-Hat (alias)    | 42        | Hi-Hat     |
| `openhat`    | Open Hi-Hat              | 46        | Hi-Hat     |
| `crash`      | Crash Cymbal 1           | 49        | Cymbal     |
| `crash2`     | Crash Cymbal 2           | 57        | Cymbal     |
| `ride`       | Ride Cymbal 1            | 51        | Cymbal     |
| `splash`     | Splash Cymbal            | 55        | Cymbal     |
| `china`      | Chinese Cymbal           | 52        | Cymbal     |
| `tom1`       | High Tom                 | 48        | Tom        |
| `tom2`       | Low-Mid Tom              | 45        | Tom        |
| `tom3`       | High Floor Tom           | 43        | Tom        |
| `tom4`       | Low Floor Tom            | 41        | Tom        |
| `clap`       | Hand Clap                | 39        | Percussion |
| `cowbell`    | Cowbell                  | 56        | Percussion |
| `tambourine` | Tambourine               | 54        | Percussion |

---

## Best Practices

### 1. Use Voices for Simultaneous Hits

Don't try to use chords - drums don't form chords:

```muslang
# Good - separate voices
drums:
  V1: kick/4 kick/4 kick/4 kick/4
  V2: r/4 snare/4 r/4 snare/4
  V3: hat/8 hat/8 hat/8 hat/8 hat/8 hat/8 hat/8 hat/8

# Even better - voices in repeating pattern
drums:
  [
    V1: kick/4 kick/4 kick/4 kick/4
    V2: r/4 snare/4 r/4 snare/4
    V3: hat/8 hat/8 hat/8 hat/8 hat/8 hat/8 hat/8 hat/8
  ] * 4

# Won't work - drums can't be chorded like pitched notes
drums: kick/4,snare/4,hat/8  # ✗ Invalid
```

### 2. Use Repeats for Patterns

Drum patterns repeat - leverage the repeat syntax:

```muslang
# Efficient
drums: [kick/4 snare/4 kick/4 snare/4] * 8

# Tedious
drums: kick/4 snare/4 kick/4 snare/4 kick/4 snare/4 ...
```

### 3. Layer Dynamics

Use dynamics for ghost notes and accents:

```muslang
drums:
  # Main snare hits loud
  @f snare/16 r/16 r/16 r/16
  # Ghost notes quiet
  @pp snare/16 @p snare/16 r/16 r/16
  # Accent again
  @ff snare/16 r/16 r/16 r/16
```

### 4. Tempo Matters

Fast patterns need appropriate tempo:

```muslang
# 16th notes at slow tempo = groovy
drums: (tempo! 90)
  [hat/16] * 16

# 16th notes at fast tempo = intense
drums: (tempo! 160)
  [hat/16] * 16
```

### 5. Name Instrument "drums" or "percussion"

These names tell the compiler to use MIDI Channel 10:

```muslang
drums: kick/4 snare/4     # ✓ Uses channel 10
percussion: kick/4 snare/4  # ✓ Also works
kit: kick/4 snare/4       # ✓ "kit" also detected

piano: kick/4 snare/4     # ✗ Won't work - not percussion
```

---

## Advanced Techniques

### Polyrhythmic Drums

Different time divisions in each voice:

```muslang
drums:
  V1: [kick/4] * 4
  V2: [(snare/8 r/8 snare/8):3] * 3  # Triplets against quarters
```

### Changing Patterns

Vary the beat throughout:

```muslang
drums: (tempo! 120)
  # Verse - simple
  [kick/4 snare/4 kick/4 snare/4] * 4
  
  # Chorus - busier
  [
    V1: kick/8 r/8 kick/16 r/16 r/8 kick/8 r/8 r/8 r/8
    V2: r/8 r/8 r/8 snare/8 r/8 r/8 r/8 snare/8
    V3: [hat/16] * 16
  ] * 4
```

### Drum Solo

Extended fill with all drums:

```muslang
drums: (tempo! 140) @ff
  # Build with toms
  tom1/16 tom1/16 tom1/16 tom1/16 
  tom2/16 tom2/16 tom2/16 tom2/16
  tom3/16 tom3/16 tom3/16 tom3/16
  tom4/16 tom4/16 tom4/16 tom4/16
  # Finish with crash
  crash/2 kick/4 snare/4
```

---

## Troubleshooting

### Problem: Drums not playing

**Check**: Instrument name must be `drums`, `percussion`, or `kit`:
```muslang
drums: kick/4 snare/4  # ✓ Works
drumset: kick/4 snare/4  # ✗ Won't be detected
```

### Problem: Multiple drums not sounding together

**Solution**: Use voices (V1, V2, etc.):
```muslang
drums:
  V1: kick/4
  V2: snare/4
  V3: hat/8 hat/8
```

### Problem: Drums too loud/soft

**Solution**: Use dynamics:
```muslang
drums: @ff kick/4  # Loud
drums: @pp hat/8   # Quiet
```

### Problem: Unknown drum name error

**Check**: Use valid drum names from the reference table:
```muslang
drums: kick/4     # ✓ Valid
drums: bassdrum/4  # ✗ Invalid name
```

---

## See Also

- [Syntax Reference](syntax_reference.md) - Complete language specification
- [Rhythm Guide](rhythm_guide.md) - Timing and rhythm notation
- [Articulation Guide](articulation_guide.md) - Dynamics and articulation
- [Examples](../examples/) - Complete musical examples including drum patterns

---

## Version

Muslang v0.1.0 - February 2026
