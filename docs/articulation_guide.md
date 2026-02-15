# Muslang Articulation Guide

Complete guide to the articulation and dynamics system in Muslang.

## Table of Contents

1. [Introduction](#introduction)
2. [Articulation Basics](#articulation-basics)
3. [Articulation Types](#articulation-types)
4. [State Behavior](#state-behavior)
5. [Dynamics System](#dynamics-system)
6. [Dynamic Transitions](#dynamic-transitions)
7. [Dynamic Accents](#dynamic-accents)
8. [Combining Articulations and Dynamics](#combining-articulations-and-dynamics)
9. [MIDI Implementation](#midi-implementation)
10. [Musical Examples](#musical-examples)

---

## Introduction

Articulation and dynamics are essential for expressive music. Muslang provides a comprehensive system for controlling:

- **Articulation**: *How* notes are played (short, smooth, accented, etc.)
- **Dynamics**: *How loud* notes are played (soft to loud)

Both systems use **persistent state** - settings remain in effect until explicitly changed.

---

## Articulation Basics

### Syntax

Articulations use the **`:` prefix**:

```muslang
:staccato   # Short, detached notes
:legato     # Smooth, connected notes
:tenuto     # Full value notes
:marcato    # Strongly accented notes
:reset      # Return to natural (default)
```

### Application

Articulations apply to **all following notes** until changed:

```muslang
piano: 
  c4/4 d4/4           # Natural (default)
  :staccato e4/4 f4/4 # Both staccato
  :legato g4/4 a4/4   # Both legato
```

---

## Articulation Types

### Natural (Default)

The default articulation - notes play at 92% of their written duration with slight separation.

```muslang
piano: c4/4 d4/4 e4/4 f4/4
```

**MIDI effect**:
- Duration: 92% of note value
- Velocity: Current dynamic level (default mf = 85)
- No special CC messages

### Staccato (:staccato)

Short, detached notes.

```muslang
piano: :staccato c4/4 d4/4 e4/4 f4/4
```

**MIDI effect**:
- Duration: 55% of note value
- Creates clear separation between notes
- Bright, bouncy character

**Musical use**: Light, playful passages, rhythmic clarity

### Legato (:legato)

Smooth, connected notes with no silence between them.

```muslang
piano: :legato c4/4 d4/4 e4/4 f4/4
```

**MIDI effect**:
- Duration: 100% of note value
- Notes overlap slightly (95% advancement)
- CC#68 (legato) sent: 127 (on)
- Very smooth transitions

**Musical use**: Lyrical melodies, expressive phrases, vocal-like lines

### Tenuto (:tenuto)

Full value, slightly emphasized notes.

```muslang
piano: :tenuto c4/4 d4/4 e4/4 f4/4
```

**MIDI effect**:
- Duration: 100% of note value
- No overlap (unlike legato)
- Slightly stronger note beginning

**Musical use**: Sustained, singing tone, emphasis without accent

### Marcato (:marcato)

Strongly accented, marked notes.

```muslang
piano: :marcato c4/4 d4/4 e4/4 f4/4
```

**MIDI effect**:
- Duration: 90% of note value
- Velocity boost: +30
- Strong, emphasized attack

**Musical use**: Dramatic emphasis, strong rhythmic accent

### Reset (:reset)

Return to natural articulation.

```muslang
piano: 
  :staccato c4/4 d4/4
  :reset e4/4 f4/4     # Back to natural
```

---

## State Behavior

### Persistent State

Articulations remain active until explicitly changed:

```muslang
piano:
  c4/4 d4/4           # Natural
  :staccato           # Switch to staccato
  e4/4 f4/4 g4/4 a4/4 # All staccato
  b4/4 c5/4           # Still staccato!
```

### Changing Articulation

Simply specify a new articulation:

```muslang
piano:
  :staccato c4/4 d4/4 # Staccato
  :legato e4/4 f4/4   # Now legato
  :marcato g4/4 a4/4  # Now marcato
  :reset b4/4 c5/4    # Natural
```

### Scope

Articulations are **per-instrument**. Each instrument tracks its own state:

```muslang
piano: :staccato c4/4 d4/4 e4/4
violin: :legato g5/4 a5/4 b5/4  # Independent state

piano: f4/4 g4/4                # Still staccato
violin: c6/4 d6/4               # Still legato
```

---

## Dynamics System

### Syntax

Dynamics use the **`@` prefix**:

```muslang
@pp     # pianissimo (very soft)
@p      # piano (soft)
@mp     # mezzo-piano (moderately soft)
@mf     # mezzo-forte (moderately loud) [DEFAULT]
@f      # forte (loud)
@ff     # fortissimo (very loud)
```

### MIDI Velocity Mapping

| Dynamic | Velocity | Loudness    |
|---------|----------|-------------|
| @pp     | 40       | Very soft   |
| @p      | 55       | Soft        |
| @mp     | 70       | Mod. soft   |
| @mf     | 85       | Mod. loud   |
| @f      | 100      | Loud        |
| @ff     | 115      | Very loud   |

### Application

Like articulations, dynamics are persistent:

```muslang
piano:
  c4/4 d4/4      # Default @mf (velocity 85)
  @p e4/4 f4/4   # Soft (velocity 55)
  @ff g4/4 a4/4  # Very loud (velocity 115)
```

### Gradual Changes

Dynamics can change smoothly between levels:

```muslang
piano:
  @p c4/4        # Start soft
  d4/4 e4/4      # Still soft
  @f f4/4        # Suddenly loud
```

---

## Dynamic Transitions

### Crescendo (@crescendo)

Gradually increase volume over following notes.

```muslang
piano:
  @p @crescendo c4/4 d4/4 e4/4 f4/4 @f g4/4
```

**Effect**:
- Starting dynamic: `@p` (velocity 55)
- Each note: +6 velocity
- Target dynamic: `@f` (velocity 100)
- Notes get progressively louder

**Typical velocities**: 55 → 61 → 67 → 73 → 79 → 85... → 100

### Diminuendo (@diminuendo / @decresc)

Gradually decrease volume over following notes.

```muslang
piano:
  @f @diminuendo g4/4 f4/4 e4/4 d4/4 @p c4/4
```

**Effect**:
- Starting dynamic: `@f` (velocity 100)
- Each note: -6 velocity
- Target dynamic: `@p` (velocity 55)
- Notes get progressively softer

**Typical velocities**: 100 → 94 → 88 → 82 → 76 → 70... → 55

### Stopping Transitions

Transitions continue until a new absolute dynamic is specified:

```muslang
piano:
  @p @crescendo c4/4 d4/4 e4/4 f4/4 g4/4 @f a4/4
  # Crescendo ends at @f
  b4/4 c5/4  # Stay at @f
```

---

## Dynamic Accents

### Sforzando (@sforzando)

Sudden, strong accent on a single note. Returns to previous dynamic immediately after.

```muslang
piano:
  @p c4/4 d4/4 @sforzando e4/4 f4/4
  # e4 is accented (+20 velocity), f4 returns to @p
```

**MIDI effect**:
- One-shot velocity boost: +20
- Example: @p (55) + sforzando = 75 velocity
- Does not change underlying dynamic state

**Musical use**: Sudden emphasis, dramatic accents, surprise

### Forte-Piano (@forte-piano)

Strong attack followed immediately by soft. "fp" in classical notation.

```muslang
piano:
  @forte-piano c4/4 d4/4 e4/4
```

**MIDI effect**:
- First note: +35 velocity boost
- Subsequent notes: Return to base dynamic
- Creates dramatic contrast

**Musical use**: Dramatic gestures, sforzato with immediate decay

### Marcato

Note: `@marcato` doesn't exist in dynamics - use `:marcato` articulation instead, which provides +30 velocity boost in addition to duration change.

---

## Combining Articulations and Dynamics

Articulations and dynamics work **independently** and can be combined:

```muslang
piano:
  # Soft staccato
  @p :staccato c4/4 d4/4 e4/4
  
  # Loud legato
  @ff :legato f4/4 g4/4 a4/4
  
  # Dynamic marcato with crescendo
  @mp :marcato @crescendo b4/4 c5/4 d5/4 @f e5/4
```

### Order Independence

Articulation and dynamic markers can appear in any order:

```muslang
piano: :staccato @f c4/4    # Same as...
piano: @f :staccato c4/4    # ...this
```

### State Interaction

- Articulations control **duration** and **attack character**
- Dynamics control **velocity/loudness**
- Both are persistent and independent
- Both can be reset separately

---

## MIDI Implementation

### Articulation to MIDI

| Articulation | Duration % | Special CC      | Velocity Mod |
|--------------|------------|-----------------|--------------|
| Natural      | 92%        | -               | -            |
| Staccato     | 55%        | -               | -            |
| Legato       | 100%       | CC#68 = 127     | -            |
| Tenuto       | 100%       | -               | -            |
| Marcato      | 90%        | -               | +30          |

### Dynamics to MIDI

| Dynamic     | Base Velocity | Transition Step | Accent Boost |
|-------------|---------------|-----------------|--------------|
| @pp         | 40            | -               | -            |
| @p          | 55            | -               | -            |
| @mp         | 70            | -               | -            |
| @mf         | 85            | -               | -            |
| @f          | 100           | -               | -            |
| @ff         | 115           | -               | -            |
| @crescendo  | -             | +6 per note     | -            |
| @diminuendo | -             | -6 per note     | -            |
| @sforzando  | -             | -               | +20          |
| @forte-piano| -             | -               | +35 (1st)    |

### Velocity Calculation Formula

```
velocity = base_dynamic + accent_boost + marcato_boost + crescendo_step * note_count
velocity = clamp(velocity, 1, 127)  # MIDI range
```

### Legato CC Events

When `:legato` is active:
- **CC#68 (Legato Switch)** = 127 at note start
- Notes overlap by 5% of duration
- Creates smooth, connected sound

### Slur Groups

Slurs `{...}` use similar technique:
- CC#68 = 127 at phrase start
- All notes overlap slightly
- CC#68 = 0 at phrase end

---

## Musical Examples

### Example 1: Dynamic Contrast

```muslang
# Demonstrates dynamic levels
piano: (tempo! 100)
  (time 4 4)
  
  # Theme at different dynamics
  @pp c4/4 e4/4 g4/4 c5/4 |  # Very soft
  @p c4/4 e4/4 g4/4 c5/4 |   # Soft
  @mp c4/4 e4/4 g4/4 c5/4 |  # Medium soft
  @mf c4/4 e4/4 g4/4 c5/4 |  # Medium loud
  @f c4/4 e4/4 g4/4 c5/4 |   # Loud
  @ff c4/4 e4/4 g4/4 c5/4 |  # Very loud
```

### Example 2: Articulation Showcase

```muslang
# Demonstrates articulation types
piano: (tempo! 120) @mf
  
  # Natural
  c4/4 d4/4 e4/4 f4/4 |
  
  # Staccato - light and bouncy
  :staccato g4/4 a4/4 b4/4 c5/4 |
  
  # Legato - smooth and singing
  :legato c5/4 b4/4 a4/4 g4/4 |
  
  # Tenuto - full value, sustained
  :tenuto f4/4 g4/4 a4/4 b4/4 |
  
  # Marcato - strong accents
  :marcato c5/4 g4/4 e4/4 c4/4 |
  
  # Back to natural
  :reset c4/1 |
```

### Example 3: Crescendo and Diminuendo

```muslang
# Dynamic transitions
piano: (tempo! 100)
  
  # Long crescendo
  @p @crescendo
  c4/4 d4/4 e4/4 f4/4 |
  g4/4 a4/4 b4/4 c5/4 |
  @f d5/2 |  # End crescendo
  
  # Long diminuendo
  @diminuendo
  c5/4 b4/4 a4/4 g4/4 |
  f4/4 e4/4 d4/4 c4/4 |
  @p c4/1 |  # End diminuendo
```

### Example 4: Sforzando Accents

```muslang
# Dramatic accents
piano: (tempo! 120) @mp
  
  # Regular pattern with accents
  c4/4 e4/4 @sforzando g4/4 e4/4 |
  c4/4 e4/4 @sforzando g4/4 e4/4 |
  
  # Forte-piano (strong then soft)
  @forte-piano c5/2 | g4/2 | c4/1 |
```

### Example 5: Combined Techniques

```muslang
# Everything together
piano: (tempo! 120)
  (time 3 4)
  
  # Theme 1: Soft and legato
  @p :legato
  c4/4 e4/4 g4/4 | c5/4 b4/4 a4/4 | g4/2. |
  
  # Theme 2: Loud and staccato
  @f :staccato
  g4/4 a4/4 b4/4 | c5/4 d5/4 e5/4 | d5/2. |
  
  # Theme 3: Crescendo with marcato
  @mp :marcato @crescendo
  c4/4 d4/4 e4/4 | f4/4 g4/4 a4/4 | @ff b4/2. |
  
  # Ending: Dramatic with accents
  :reset @f
  @sforzando c5/4 g4/4 e4/4 | @sforzando c4/2. |
```

### Example 6: Expressive Melody

```muslang
# A lyrical melody using articulation and dynamics
piano: (tempo! 80)
  (key f 'major)
  
  # Opening phrase - soft and smooth
  @p :legato
  f4/4 g4/4 a4/4 b4-/4 |
  c5/2 a4/4 f4/4 |
  
  # Building phrase - crescendo
  @crescendo
  g4/4 a4/4 b4-/4 c5/4 |
  @mf d5/4 c5/4 b4-/4 a4/4 |
  
  # Climax - loud with accents
  @f @sforzando g4/4 :marcato f5/2 e5/4 |
  
  # Ending - diminuendo to soft
  :legato @diminuendo
  d5/4 c5/4 b4-/4 a4/4 |
  @p g4/2 f4/2 |
  f4/1 |
```

---

## Best Practices

### 1. Use Natural as Baseline

Start with natural articulation and add articulation only where musically necessary:

```muslang
# Good - articulation for emphasis
piano: c4/4 d4/4 :staccato e4/4 :reset f4/4

# Overdone - unnecessary articulation changes
piano: :tenuto c4/4 :legato d4/4 :staccato e4/4 :tenuto f4/4
```

### 2. Dynamic Contrast

Don't stay at one dynamic level - use contrast for interest:

```muslang
# Good - varied dynamics
piano: @p c4/2 @f g4/2 @mp e4/1

# Boring - no contrast
piano: @mf c4/2 g4/2 e4/1
```

### 3. Smooth Transitions

Use crescendo/diminuendo for gradual changes rather than sudden jumps:

```muslang
# Good - smooth crescendo
piano: @p @crescendo c4/4 d4/4 e4/4 f4/4 @f g4/2

# Jarring - sudden change
piano: @p c4/4 d4/4 e4/4 f4/4 @ff g4/2
```

### 4. Reset When Needed

Use `:reset` to return to baseline, especially after special articulations:

```muslang
# Good - explicit reset
piano: :marcato c4/4 d4/4 :reset e4/4 f4/4

# Unclear - marcato continues
piano: :marcato c4/4 d4/4 e4/4 f4/4
```

### 5. Instrument-Appropriate Articulation

Some articulations suit certain instruments better:

```muslang
# Good - staccato strings
violin: :staccato g5/8 g5/8 g5/8 g5/8

# Good - legato woodwinds
flute: :legato c5/4 d5/4 e5/4 f5/4

# Consider - staccato on sustained instruments
organ: :staccato c4/4 d4/4 e4/4 f4/4  # May not be effective
```

---

## Troubleshooting

### Problem: Notes sound disconnected even with legato

**Solution**: Use slur groups `{}` for tighter connection:
```muslang
piano: :legato {c4/4 d4/4 e4/4 f4/4}
```

### Problem: Crescendo not audible enough

**Solution**: Use wider dynamic range:
```muslang
# Wider range - more noticeable
piano: @pp @crescendo c4/4 d4/4 e4/4 f4/4 @ff g4/2
```

### Problem: Accents not strong enough

**Solution**: Combine accent with louder base dynamic or use marcato:
```muslang
piano: @f @sforzando c4/4  # Louder accent
piano: :marcato c4/4        # Strong articulation
```

### Problem: Staccato too short/choppy

**Solution**: Use tenuto instead, or adjust tempo:
```muslang
piano: :tenuto c4/4 d4/4 e4/4 f4/4  # Fuller than staccato
piano: (tempo! 80) :staccato c4/4 d4/4  # Slower = less choppy
```

---

## Advanced Techniques

### Terraced Dynamics

Classical baroque style with sudden dynamic changes:

```muslang
piano: (tempo! 120)
  @f c4/4 d4/4 e4/4 f4/4 |
  @p c4/4 d4/4 e4/4 f4/4 |
  @f g4/4 a4/4 b4/4 c5/4 |
  @p g4/4 a4/4 b4/4 c5/4 |
```

### Echo Effects

Repeat phrases at softer dynamics:

```muslang
piano:
  @f c4/4 e4/4 g4/4 c5/4 |
  @mp c4/4 e4/4 g4/4 c5/4 |  # Echo
  @pp c4/4 e4/4 g4/4 c5/4 |  # Distant echo
```

### Crescendo/Diminuendo Arcs

Build and release tension:

```muslang
piano:
  # Build up
  @p @crescendo c4/4 d4/4 e4/4 f4/4 @f g4/2 |
  
  # Release
  @diminuendo f4/4 e4/4 d4/4 c4/4 @p c4/1 |
```

### Mixed Articulation

Different articulations in different voices:

```muslang
piano:
  V1: :staccato c5/4 c5/4 c5/4 c5/4
  V2: :legato c3/1
```

---

## See Also

- [Syntax Reference](syntax_reference.md) - Complete language specification
- [Rhythm Guide](rhythm_guide.md) - Timing and rhythm notation
- [Ornaments Guide](ornaments_guide.md) - Trills, mordents, and turns
- [Examples](../examples/) - Complete musical examples

---

## Version

Muslang v0.1.0 - February 2026
