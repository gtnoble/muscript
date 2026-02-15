# Muslang Ornaments Guide

Complete guide to ornaments and musical embellishments in Muslang.

## Table of Contents

1. [Introduction](#introduction)
2. [Ornament Basics](#ornament-basics)
3. [Trill](#trill)
4. [Mordent](#mordent)
5. [Turn](#turn)
6. [Tremolo](#tremolo)
7. [Key Signature Awareness](#key-signature-awareness)
8. [Ornament Expansion](#ornament-expansion)
9. [Musical Examples](#musical-examples)
10. [Best Practices](#best-practices)

---

## Introduction

Ornaments are decorative musical embellishments that add expressiveness and flourish to melodies. Muslang provides four main ornament types:

- **Trill**: Rapid alternation between a note and its upper neighbor
- **Mordent**: Quick dip to lower neighbor and back
- **Turn**: Graceful rotation through neighboring notes
- **Tremolo**: Rapid repetition of the same note

All ornaments use the **`%` prefix** and are **key-signature aware**.

---

## Ornament Basics

### Syntax

```muslang
%ornament_type note
```

The ornament marker applies to the **immediately following note**.

### Available Ornaments

| Ornament | Symbol     | Effect                               |
|----------|------------|--------------------------------------|
| Trill    | `%trill`   | Rapid note-upper alternation         |
| Mordent  | `%mordent` | Quick note-lower-note figure         |
| Turn     | `%turn`    | Upper-note-lower-note figure         |
| Tremolo  | `%tremolo` | Rapid repetition of same note        |

### Examples

```muslang
piano:
  V1: %trill c4/2      # Trill on C4
      %mordent d4/4    # Mordent on D4
      %turn e4/4       # Turn on E4
      %tremolo g4/1    # Tremolo on G4
```

---

## Trill

A **trill** is a rapid alternation between a note and its **upper scale neighbor**.

### Notation

```muslang
%trill note
```

### How It Works

The trill alternates between:
1. **Main note** (the written note)
2. **Upper neighbor** (next note in the scale)

The alternation happens at **32nd note** speed (8 notes per quarter note).

### Example

```muslang
# Simple trill
piano: (key c 'major)
  V1: %trill c4/2
```

**Expansion** (in C major, upper neighbor is D):
```
c4/32 d4/32 c4/32 d4/32 c4/32 d4/32 c4/32 d4/32  # (continues for half note duration)
```

### Musical Context

```muslang
# Trill in a melody
piano: (key g 'major) (tempo! 120)
  V1: g4/4 a4/4 %trill b4/2 |
      a4/4 g4/4 f4+/4 e4/4 |
```

### Duration Effect

Trills expand based on the main note's duration:
- Quarter note: ~8 alternations
- Half note: ~16 alternations
- Whole note: ~32 alternations

---

## Mordent

A **mordent** is a quick ornament that dips to the **lower scale neighbor** and returns.

### Notation

```muslang
%mordent note
```

### How It Works

The mordent creates a three-note figure:
1. **Main note** (very brief)
2. **Lower neighbor**
3. **Main note** (full duration)

The first two notes are 32nd notes, the last gets the remaining duration.

### Example

```muslang
# Simple mordent
piano: (key c 'major)
  V1: %mordent c4/4
```

**Expansion** (in C major, lower neighbor is B):
```
c4/32  # Quick main note
b3/32  # Lower neighbor
c4/4   # Main note (minus time stolen by first two)
```

### Musical Context

```muslang
# Mordents in Bach-style melody
piano: (key d 'major) (tempo! 100)
  V1: @mf d4/4 %mordent e4/4 f4+/4 %mordent g4/4 |
      a4/2 %mordent d5/2 |
```

### Visual Effect

Creates a quick "snap" or "bite" before settling on the main note.

---

## Turn

A **turn** is an elegant ornament that rotates through neighboring notes.

### Notation

```muslang
%turn note
```

### How It Works

The turn creates a four-note figure:
1. **Upper neighbor**
2. **Main note**
3. **Lower neighbor**
4. **Main note**

All four notes are equal duration, fitting into the main note's time.

### Example

```muslang
# Simple turn
piano: (key c 'major)
  V1: %turn c4/4
```

**Expansion** (in C major):
```
d4/16   # Upper neighbor (D)
c4/16   # Main note (C)
b3/16   # Lower neighbor (B)
c4/16   # Main note (C)
```

### Musical Context

```muslang
# Classical-style melody with turns
piano: (key f 'major) (tempo! 90)
  V1: :legato @mp
      f4/4 g4/4 %turn a4/2 |
      b4-/4 a4/4 g4/4 %turn f4/2 |
```

### Visual Effect

Creates a graceful, rotating gesture around the main note.

---

## Tremolo

A **tremolo** is a rapid repetition of the same note.

### Notation

```muslang
%tremolo note
```

### How It Works

The tremolo repeats the note at **16th note** speed (4 notes per quarter note).

### Example

```muslang
# Simple tremolo
piano:
  V1: %tremolo c4/1
```

**Expansion**:
```
c4/16 c4/16 c4/16 c4/16  # (continues for whole note = 16 repetitions)
```

### Musical Context

```muslang
# Tense, suspenseful passage
piano: (tempo! 120)
  V1: @pp @crescendo
      %tremolo c4/1 |
      %tremolo c4/1 |
      @f c4/4 e4/4 g4/4 c5/4 |
```

### Duration Effect

Tremolo repetitions based on main note duration:
- Quarter note: 4 repetitions
- Half note: 8 repetitions
- Whole note: 16 repetitions

### Bowed Tremolo vs Fingered Tremolo

Muslang's tremolo is a **single-note tremolo** (bowed tremolo on strings). For **fingered tremolo** (alternating between two notes), use a fast alternation pattern:

```muslang
# Fingered tremolo between C and E
piano:
  V1: c4/16 e4/16 c4/16 e4/16 c4/16 e4/16 c4/16 e4/16
      c4/16 e4/16 c4/16 e4/16 c4/16 e4/16 c4/16 e4/16
```

---

## Key Signature Awareness

All ornaments respect the **current key signature** when determining neighboring notes.

### Example: C Major

```muslang
piano: (key c 'major)
  V1: %trill c4/4   # Trills C-D (D natural)
      %trill f4/4   # Trills F-G (no sharps in C major)
```

### Example: G Major (F♯)

```muslang
piano: (key g 'major)
  V1: %trill f4+/4  # Trills F♯-G (upper neighbor is G)
      %mordent g4/4 # Mordent G-F♯-G (lower neighbor is F♯)
```

### Example: D Minor (B♭)

```muslang
piano: (key d 'minor)
  V1: %trill d4/4   # Trills D-E (E natural in D minor)
      %turn b4-/4   # Turn: C-B♭-A-B♭
```

### Chromatic Neighbors

Neighbors are calculated **diatonically** (by scale degree), not chromatically:

```muslang
# In C major
piano: (key c 'major)
  V1: %trill e4/4   # E-F (not E-F♯), F is natural in C major
```

### Accidentals on Main Note

If the main note has an accidental, neighbors are still calculated from the scale:

```muslang
# C major, but note is altered
piano: (key c 'major)
  V1: %trill c4+/4  # C♯-D (trill uses D from scale)
```

---

## Ornament Expansion

### How Ornaments are Compiled

During compilation, ornament markers are **expanded** into sequences of regular notes:

```
%trill c4/2  →  c4/32 d4/32 c4/32 d4/32 ... (alternating for half note duration)
```

This expansion happens in the **semantic analysis phase**, before MIDI generation.

### Expansion Details

#### Trill Expansion

- **Rate**: 32nd notes (8 notes per quarter note)
- **Alternation**: Main note and upper neighbor
- **Duration**: Fills entire main note duration
- **Starting note**: Begins on main note

#### Mordent Expansion

- **Figure**: Main-lower-main
- **Timing**: 
  - First note: 32nd note (main)
  - Second note: 32nd note (lower neighbor)
  - Third note: Remaining duration (main)

#### Turn Expansion

- **Figure**: Upper-main-lower-main
- **Timing**: Four equal divisions of main note duration
- **Example for quarter note**: 4 × 16th notes

#### Tremolo Expansion

- **Rate**: 16th notes (4 notes per quarter note)
- **Repetition**: Same note repeated
- **Duration**: Fills entire main note duration

### Scale Degree Calculation

Neighbors are found by:
1. Looking at current key signature
2. Finding pitch class in scale
3. Moving up or down one scale degree
4. Handling octave boundaries

Example in C major:
- C → D (up), B (down)
- E → F (up), D (down)
- B → C (up, crosses octave), A (down)

---

## Musical Examples

### Example 1: Classical Trill

```muslang
# Ornate Baroque-style melody
piano: (key d 'major) (tempo! 100)
  V1: @mf :legato
      d4/8 f4+/8 %trill a4/4 g4/8 f4+/8 |
      e4/8 d4/8 %trill c4+/2 |
```

### Example 2: Mordent Accents

```muslang
# Crisp articulation with mordents
piano: (key g 'major) (tempo! 120)
  V1: :staccato @f
      %mordent g4/8 g4/8 %mordent d5/8 d5/8 |
      %mordent b4/4 %mordent g4/4 |
```

### Example 3: Turn Embellishment

```muslang
# Elegant melody with turns
piano: (key f 'major) (tempo! 90)
  V1: :legato @mp
      f4/4 %turn a4/4 c5/4 %turn f5/4 |
      e5/4 d5/4 c5/4 %turn b4-/4 |
      a4/2 %turn g4/2 | f4/1 |
```

### Example 4: Tremolo Suspense

```muslang
# Building tension with tremolo
piano: (tempo! 120) (key c 'minor)
  V1: @pp @crescendo
      %tremolo c4/2 %tremolo e4-/2 |
      %tremolo g4/2 %tremolo c5/2 |
      @ff c5/4 g4/4 e4-/4 c4/4 |
```

### Example 5: Mixed Ornaments

```muslang
# Showcase different ornaments
piano: (key d 'major) (tempo! 110)
  V1: @mf
      d4/4 %trill f4+/4 a4/4 %mordent d5/4 |
      %turn c5+/4 b4/4 a4/4 g4/4 |
      %tremolo f4+/2 e4/4 d4/4 |
```

### Example 6: Ornaments with Dynamics

```muslang
# Expressive phrasing
piano: (key e- 'major) (tempo! 80)
  V1: @p :legato
      e4-/8 g4/8 %trill b4-/4. a4-/8 |
      
      @mp
      g4/8 f4/8 %turn e4-/2 |
      
      @f %mordent b4-/4 %trill e5-/2 d5/4 |
      
      @p @diminuendo
      c5/4 b4-/4 a4-/4 %turn g4/4 |
      @pp e4-/1 |
```

### Example 7: Bach-style Ornamentation

```muslang
# Baroque counterpoint
piano: (key g 'major) (tempo! 100)
  V1: 
    :legato @mf
    %mordent g5/4 f5+/8 e5/8 %turn d5/4 c5/8 b4/8 |
    %trill a4/2. g4/4 |
  
  V2:
    :legato @mp
    g3/4 a3/4 b3/4 c4/4 |
    %turn d4/2 g3/2 |
```

### Example 8: Romantic Expressiveness

```muslang
# Lyrical romantic melody
piano: (key a- 'major) (tempo! 70)
  V1: :legato @p
      e4-/4 %turn a4-/4 c5/4. b4-/8 |
      
      @crescendo
      %trill a4-/4 g4/8 f4/8 e4-/4 d4-/4 |
      
      @mf
      %tremolo c4/2 %mordent d4-/4 e4-/4 |
      
      @diminuendo
      f4/4 %turn e4-/4 d4-/4 c4/4 |
      @pp a3-/1 |
```

---

## Best Practices

### 1. Context Matters

Use ornaments where they enhance the musical line, not everywhere:

```muslang
# Good - selective ornamentation
piano:
  V1: c4/4 d4/4 %trill e4/2

# Overdone - too many ornaments
piano:
  V1: %trill c4/4 %mordent d4/4 %turn e4/4 %tremolo f4/4
```

### 2. Duration Considerations

Give ornaments enough time to be heard:

```muslang
# Good - quarter note or longer
piano:
  V1: %trill c4/4

# Questionable - sixteenth note trill is extremely fast
piano:
  V1: %trill c4/16
```

### 3. Key Signature Awareness

Remember ornaments use scale neighbors:

```muslang
# In G major, F is sharp
piano: (key g 'major)
  V1: %trill e4/4  # Will trill E-F♯ (not E-F)
```

### 4. Dynamics with Ornaments

Ornaments inherit current dynamic level:

```muslang
# Soft trill
piano:
  V1: @p %trill c4/2

# Loud, emphatic mordent
piano:
  V1: @ff %mordent g4/4
```

### 5. Articulation Interaction

Ornaments expand into multiple notes that inherit articulation:

```muslang
# Staccato trill - each alternation is staccato
piano:
  V1: :staccato %trill c4/4

# Legato turn - smooth rotation
piano:
  V1: :legato %turn d4/4
```

---

## Advanced Techniques

### Ornaments in Chords

Ornament the top note of a chord:

```muslang
# Not directly supported - ornament applies to following whole chord
# Workaround: Use voices
piano:
  V1: %trill g4/2
  V2: c4/2,e4/2
```

### Chain Ornaments

Multiple ornaments in sequence:

```muslang
piano:
  V1: %trill c4/4 %mordent d4/4 %turn e4/4 %trill f4/4
```

### Crescendo with Tremolo

Building tension:

```muslang
piano:
  V1: @pp @crescendo %tremolo c4/1 @ff c4/4
```

### Ornaments Across Key Changes

```muslang
piano:
  (key c 'major)
  V1: %trill e4/4 f4/4 |  # Trill E-F
  
  (key g 'major)
  V1: %trill e4/4 f4+/4 |  # Trill E-F♯ (F is sharp in G)
```

---

## Troubleshooting

### Problem: Trill sounds wrong

**Check**: Key signature - neighbors come from current scale
```muslang
piano: (key d 'major)
  V1: %trill f4+/4  # F♯-G (not F♯-F)
```

### Problem: Ornament too fast/slow

**Adjust**: Use longer note duration for slower ornament
```muslang
# Too fast
piano: (tempo! 200)
  V1: %trill c4/16

# Better
piano: (tempo! 120)
  V1: %trill c4/4
```

### Problem: Mordent sounds choppy

**Solution**: Use legato articulation
```muslang
piano:
  V1: :legato %mordent d4/4
```

### Problem: Can't hear tremolo

**Check**: Volume - use appropriate dynamic
```muslang
piano:
  V1: @f %tremolo c4/2  # Loud enough to hear
```

---

## Comparison with Traditional Notation

### Ornament Symbols

| Traditional | Muslang      | Description          |
|-------------|--------------|----------------------|
| tr          | `%trill`     | Trill                |
| mor or ~    | `%mordent`   | Mordent              |
| ∞ or ⟲      | `%turn`      | Turn                 |
| trem        | `%tremolo`   | Tremolo              |

### Differences

1. **Muslang ornaments have fixed speed**: Trills are always 32nd notes, tremolo always 16th notes
2. **No inverted mordent**: Muslang mordent always goes to lower neighbor
3. **Turn always starts above**: No inverted turn (starting below)
4. **Tremolo is single-note only**: For two-note tremolo, spell it out

---

## See Also

- [Syntax Reference](syntax_reference.md) - Complete language specification
- [Articulation Guide](articulation_guide.md) - Articulation and dynamics
- [Rhythm Guide](rhythm_guide.md) - Timing and rhythm notation
- [Examples](../examples/) - Complete musical examples

---

## Version

Muslang v0.1.0 - February 2026
