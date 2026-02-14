"""
Configuration and constants for Muslang music DSL.

This module contains all configuration parameters for MIDI generation, including:
- MIDI timing and resolution
- Default articulation and note duration settings
- Dynamic level velocity mappings
- Articulation duration percentages
- MIDI Control Change (CC) numbers
- General MIDI defaults

All constants are tunable for different expressive interpretations.
"""

# ============================================================================
# MIDI Configuration
# ============================================================================

DEFAULT_MIDI_PPQ = 480
"""
Pulses Per Quarter note (PPQ) - MIDI timing resolution.

Higher values provide more precise timing. Standard values are 96, 192, 384, or 480.
480 PPQ provides excellent resolution for complex rhythms and expressive timing.
"""

DEFAULT_TEMPO = 120
"""
Default tempo in beats per minute (BPM).

This is used when no tempo directive is specified in the composition.
120 BPM is a common moderate tempo (allegretto).
"""

DEFAULT_VELOCITY = 85
"""
Default MIDI velocity (volume/intensity) for notes.

Range: 0-127, where 0 is silent and 127 is maximum.
85 corresponds to mezzo-forte (mf) dynamic level.
"""

# ============================================================================
# Default Articulation
# ============================================================================

NATURAL_DURATION_PERCENT = 92
"""
Duration percentage for natural (unmarked) notes.

Natural articulation plays notes at 92% of their written duration, creating
a slight separation between notes while maintaining a connected feel.
This prevents notes from bleeding into each other.
"""

DEFAULT_NOTE_DURATION = 1
"""
Default note duration when not specified.

1 = whole note, 2 = half note, 4 = quarter note, etc.
Whole note (1) provides maximum flexibility for relative duration specification.
"""

# ============================================================================
# Dynamic Level Velocities
# ============================================================================

VELOCITY_PP = 40
"""Velocity for pianissimo (pp) - very soft."""

VELOCITY_P = 55
"""Velocity for piano (p) - soft."""

VELOCITY_MP = 70
"""Velocity for mezzo-piano (mp) - moderately soft."""

VELOCITY_MF = 85
"""Velocity for mezzo-forte (mf) - moderately loud (default)."""

VELOCITY_F = 100
"""Velocity for forte (f) - loud."""

VELOCITY_FF = 115
"""Velocity for fortissimo (ff) - very loud."""

# ============================================================================
# Accent Boosts
# ============================================================================

SFORZANDO_BOOST = 20
"""
Velocity increase for sforzando (sfz) accent.

Sforzando is a sudden strong accent on a single note or chord.
+20 velocity provides a noticeable but not overwhelming accent.
"""

MARCATO_BOOST = 30
"""
Velocity increase for marcato accent.

Marcato is a strong accent with slight separation.
+30 velocity creates a more pronounced accent than sforzando.
"""

FORTE_PIANO_BOOST = 35
"""
Velocity increase for forte-piano (fp) accent.

Forte-piano means loud followed immediately by soft.
The initial attack gets this boost, then immediately drops to current dynamic.
"""

# ============================================================================
# Articulation Durations
# ============================================================================

STACCATO_DURATION = 55
"""
Duration percentage for staccato notes.

Staccato notes are short and detached, played at about half their written duration.
55% provides clear separation while remaining musical.
"""

LEGATO_DURATION = 100
"""
Duration percentage for legato notes.

Legato notes are smooth and connected, playing their full duration with overlap.
100% means notes extend to the next note onset, creating a seamless connection.
"""

TENUTO_DURATION = 100
"""
Duration percentage for tenuto notes.

Tenuto notes are held for their full value, slightly emphasized but not accented.
100% gives full duration, distinguishing it from natural articulation.
"""

MARCATO_DURATION = 90
"""
Duration percentage for marcato notes.

Marcato notes are accented and slightly detached.
90% provides slight separation while emphasizing the note through increased velocity.
"""

# ============================================================================
# Dynamic Transitions
# ============================================================================

DYNAMIC_TRANSITION_STEP = 6
"""
Velocity change per note during crescendo/diminuendo.

Each note in a crescendo increases by this amount; diminuendo decreases.
6 velocity units provides smooth, audible gradual changes.
Adjust this value for more gradual (lower) or more dramatic (higher) transitions.
"""

# ============================================================================
# Grace Notes
# ============================================================================

GRACE_NOTE_DURATION_RATIO = 0.05
"""
Grace note duration as a ratio of quarter note.

Grace notes are quick ornamental notes before a main note.
0.05 means 5% of a quarter note (very short, about a 64th note at 480 PPQ).
This creates the characteristic "crushed" sound of grace notes.
"""

# ============================================================================
# Tremolo
# ============================================================================

TREMOLO_RATE = 16
"""
Tremolo repetition rate (notes per quarter note).

Tremolo rapidly repeats a note or alternates between notes.
16 means 16th notes (common for tremolo).
Adjust to 32 for faster tremolo or 8 for slower.
"""

# ============================================================================
# MIDI Control Change (CC) Numbers
# ============================================================================

CC_MODULATION = 1
"""CC#1 - Modulation wheel (vibrato/tremolo effect)."""

CC_EXPRESSION = 11
"""CC#11 - Expression controller (fine dynamics control)."""

CC_PAN = 10
"""CC#10 - Pan (stereo position: 0=left, 64=center, 127=right)."""

CC_SUSTAIN = 64
"""CC#64 - Sustain pedal (0=off, 127=on)."""

CC_LEGATO = 68
"""CC#68 - Legato footswitch (enables legato/portamento on some synths)."""

CC_PORTAMENTO_TIME = 5
"""CC#5 - Portamento time (controls glide speed between notes)."""

CC_PORTAMENTO_SWITCH = 65
"""CC#65 - Portamento on/off switch (0=off, 127=on)."""

# ============================================================================
# General MIDI Defaults
# ============================================================================

GM_DRUM_CHANNEL = 9
"""
MIDI channel for percussion/drums (0-indexed).

General MIDI reserves channel 10 (1-indexed) or channel 9 (0-indexed) for drums.
On this channel, note numbers map to specific drum sounds rather than pitches.
"""

# ============================================================================
# MIDI Value Ranges
# ============================================================================

MIDI_MIN_NOTE = 0
"""Minimum MIDI note number (C-1)."""

MIDI_MAX_NOTE = 127
"""Maximum MIDI note number (G9)."""

MIDI_MIN_VELOCITY = 0
"""Minimum MIDI velocity (silent)."""

MIDI_MAX_VELOCITY = 127
"""Maximum MIDI velocity (maximum volume)."""

MIDI_MIN_CHANNEL = 0
"""Minimum MIDI channel (0-indexed)."""

MIDI_MAX_CHANNEL = 15
"""Maximum MIDI channel (0-indexed, corresponds to channel 16 in 1-indexed notation)."""

# ============================================================================
# Timing Constants
# ============================================================================

WHOLE_NOTE = 1
"""Whole note duration value."""

HALF_NOTE = 2
"""Half note duration value."""

QUARTER_NOTE = 4
"""Quarter note duration value."""

EIGHTH_NOTE = 8
"""Eighth note duration value."""

SIXTEENTH_NOTE = 16
"""Sixteenth note duration value."""

THIRTY_SECOND_NOTE = 32
"""Thirty-second note duration value."""

SIXTY_FOURTH_NOTE = 64
"""Sixty-fourth note duration value."""

VALID_DURATIONS = [1, 2, 4, 8, 16, 32, 64]
"""List of valid note durations in the system."""

DOT_MULTIPLIER = 1.5
"""
Multiplier for dotted notes.

A dot adds half the note's value (e.g., dotted quarter = 1.5 * quarter).
"""

# ============================================================================
# Octave Ranges
# ============================================================================

MIN_OCTAVE = 0
"""Minimum supported octave number (MIDI notes 0-11)."""

MAX_OCTAVE = 10
"""Maximum supported octave number (MIDI notes 120-127)."""

DEFAULT_OCTAVE = 4
"""
Default octave when not specified.

Octave 4 contains middle C (C4 = MIDI note 60), which is a common reference point.
"""

# ============================================================================
# Slide/Glissando Settings
# ============================================================================

SLIDE_STEPS = 20
"""
Number of pitch bend steps for chromatic slides.

More steps create smoother slides but generate more MIDI events.
20 steps provides smooth glissando without overwhelming the MIDI stream.
"""

PITCH_BEND_RANGE = 2
"""
Default pitch bend range in semitones.

Most synthesizers default to ±2 semitones for pitch bend.
This affects the calculation of pitch bend values for slides.
"""

PITCH_BEND_CENTER = 8192
"""
Center position for pitch bend (no bend).

MIDI pitch bend is a 14-bit value (0-16383), with 8192 representing no bend.
"""

PITCH_BEND_MIN = 0
"""Minimum pitch bend value (maximum downward bend)."""

PITCH_BEND_MAX = 16383
"""Maximum pitch bend value (maximum upward bend)."""
