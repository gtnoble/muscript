# Lo-Fi Hip-Hop Beat (Macro Source)
# Inspired by chill lo-fi study/beats genre
# Generate: m4 examples/lofi_beat.mus.m4 > examples/lofi_beat.mus

define(`REPEAT', `ifelse($1, `0', `', `$2`'REPEAT(decr($1), `$2')')')dnl

# ==============================
# Electric Piano/Rhodes Chords (lush, jazzy)
# 2-bar patterns with jazz voicings
# Use + for sharps, - for flats
# ==============================

# C major 9 - D minor 7 - E minor 7 - F major 9 (comma-separated chords)
define(`CHORD_A1', `c3/4.,e3/4.,g3/4.,b3/4.,d4/4. r/8 c3/8,e3/8,g3/8,b3/8,d4/8 r/8 r/4 r/4')dnl
define(`CHORD_A2', `d3/4.,f3/4.,a3/4.,c4/4. r/8 d3/8,f3/8,a3/8,c4/8 r/8 r/4 r/4')dnl
define(`CHORD_B1', `e3/4.,g3/4.,b3/4.,d4/4. r/8 e3/8,g3/8,b3/8,d4/8 r/8 r/4 r/4')dnl
define(`CHORD_B2', `f3/4.,a3/4.,c4/4.,e4/4.,g4/4. r/8 f3/8,a3/8,c4/8,e4/8 r/8 r/4 r/4')dnl

# G major 7 - A minor 7 - D minor 7 - G7
define(`CHORD_C1', `g3/4.,b3/4.,d4/4.,f4+/4. r/8 g3/8,b3/8,d4/8,f4+/8 r/8 r/4 r/4')dnl
define(`CHORD_C2', `a3/4.,c4/4.,e4/4.,g4/4. r/8 a3/8,c4/8,e4/8,g4/8 r/8 r/4 r/4')dnl
define(`CHORD_D1', `d3/4.,f3/4.,a3/4.,c4/4. r/8 d3/8,f3/8,a3/8,c4/8 r/8 r/4 r/4')dnl
define(`CHORD_D2', `g3/4.,b3/4.,d4/4.,f4/4. r/8 g3/8,b3/8,d4/8,f4/8 r/8 r/4 r/4')dnl

# E minor 9 - A7 - D minor 7 - G7 (bridge)
define(`CHORD_E1', `e3/4.,g3/4.,b3/4.,d4/4.,f4+/4. r/8 e3/8,g3/8,b3/8,d4/8 r/8 r/4 r/4')dnl
define(`CHORD_E2', `a3/4.,c4+/4.,e4/4.,g4/4.,b4+/4. r/8 a3/8,c4+/8,e4/8,g4/8 r/8 r/4 r/4')dnl
define(`CHORD_F1', `d3/4.,f3/4.,a3/4.,c4/4. r/8 d3/8,f3/8,a3/8,c4/8 r/8 r/4 r/4')dnl
define(`CHORD_F2', `g3/4.,b3/4.,d4/4.,f4/4.,a4+/4. r/8 g3/8,b3/8,d4/8,f4/8 r/8 r/4 r/4')dnl

# ==============================
# Bass (1 bar each)
# Smooth, sustained bass notes
# ==============================
define(`BASS_C', `c2/2. r/16 c2/16')dnl
define(`BASS_D', `d2/2. r/16 d2/16')dnl
define(`BASS_E', `e2/2. r/16 e2/16')dnl
define(`BASS_F', `f2/2. r/16 f2/16')dnl
define(`BASS_G', `g2/2. r/16 g2/16')dnl
define(`BASS_A', `a2/2. r/16 a2/16')dnl
define(`BASS_GS', `g1+/2. r/16 g1+/16')dnl
define(`BASS_GL', `g1/2. r/16 g1/16')dnl

# ==============================
# Lo-Fi Drums (1 bar each)
# Boom-bap style with laid-back feel
# ==============================
define(`KICK_A', `kick/8 r/8 kick/8 r/4 r/8 kick/8 r/4 r/8')dnl
define(`KICK_B', `kick/8 r/16 kick/16 r/8 kick/8 r/4 r/8 kick/8 r/8')dnl
define(`KICK_C', `kick/4 r/4 kick/8 r/8 kick/8 r/8 r/4')dnl

define(`SNARE_A', `r/4 snare/8 r/8 r/4 snare/8 r/8 r/8')dnl
define(`SNARE_B', `r/4 snare/16 r/16 r/4 snare/8 r/8 r/8')dnl

define(`HAT_A', `hat/16 r/8 hat/16 r/8 hat/16 r/8 hat/16 r/8 hat/16 r/8 hat/16 r/8 hat/16 r/8')dnl
define(`HAT_B', `hat/16 r/16 hat/16 r/8 hat/16 r/16 hat/16 r/8 hat/16 r/16 hat/16 r/8 hat/16 r/16 hat/16 r/8')dnl
define(`HAT_O', `hat/16 r/8 hat/16 r/8 openhat/16 r/8 hat/16 r/8 hat/16 r/8 hat/16 r/8 hat/16 r/8')dnl

define(`FILL_END', `kick/4 snare/4 r/4 hat/16 tom1/16 tom2/16 kick/16')dnl

# ==============================
# Melody fragments (2 bars each)
# Simple, nostalgic, lo-fi style
# ==============================
define(`MELODY_A', `r/4 e5/16 g5/16 r/8 g5/8 r/8 e5/4 r/8 d5/8')dnl
define(`MELODY_B', `r/2 d5/8 e5/8 g5/8 r/8 a5/4 r/8')dnl
define(`MELODY_C', `g5/8 r/8 a5/8 r/8 g5/8 e5/4 r/8 d5/2')dnl
define(`MELODY_D', `c5/4. r/16 d5/8 e5/8 g5/2 r/4')dnl

# ==============================
# Intro Section (4 bars)
# ==============================
electric_piano_1: (tempo! 70) (time 4 4) (key c 'major)
  V1: @mp :legato CHORD_A1 | CHORD_A2 | CHORD_B1 | CHORD_B2 |

# ==============================
# Piano Lead - 52 bars
# Intro 4 + A 16 + B 16 + C 8 + Outro 8
# ==============================
electric_piano_2: (tempo! 70) (time 4 4) (key c 'major)
  V1: @mp :legato REPEAT(4, `CHORD_A1 | CHORD_A2 | CHORD_B1 | CHORD_B2 | ')
  
  V1: @mf REPEAT(4, `CHORD_C1 | CHORD_C2 | CHORD_D1 | CHORD_D2 | ')
  
  V1: @mp CHORD_E1 | CHORD_E2 | CHORD_F1 | CHORD_F2 |
  V1: @mf CHORD_E1 | CHORD_E2 | CHORD_F1 | CHORD_F2 |
  
  V1: @diminuendo REPEAT(2, `CHORD_A1 | CHORD_A2 | CHORD_B1 | CHORD_B2 | ')

# ==============================
# Bass
# ==============================
bass: (tempo! 70) (time 4 4) (key c 'major)
  V1: @mp r/1 | r/1 |
  
  V1: @mp REPEAT(4, `BASS_C | BASS_D | BASS_E | BASS_F | ')
  
  V1: @mf REPEAT(4, `BASS_G | BASS_A | BASS_D | BASS_G | ')
  
  V1: @mp BASS_E | BASS_GS | BASS_D | BASS_GL |
  V1: @mf BASS_E | BASS_GS | BASS_D | BASS_GL |
  
  V1: @diminuendo REPEAT(2, `BASS_C | BASS_D | BASS_E | BASS_F | ')

# ==============================
# Drums
# ==============================
drums: (tempo! 70) (time 4 4)
  V1: @mp r/1 | r/1 | r/2 KICK_A | KICK_A |
  V2: @p r/1 | r/1 | r/2 SNARE_A | SNARE_A |
  V3: r/1 | r/1 | r/2 HAT_A | HAT_A |
  
  V1: @mp REPEAT(2, `KICK_A | KICK_A | KICK_B | KICK_A | ') REPEAT(2, `KICK_B | KICK_A | KICK_C | KICK_A | ')
  V2: REPEAT(16, `SNARE_A ')
  V3: REPEAT(8, `HAT_A ') REPEAT(8, `HAT_B ')
  
  V1: @mf REPEAT(4, `KICK_B | KICK_A | KICK_B | KICK_A | ')
  V2: REPEAT(4, `SNARE_A | SNARE_A | SNARE_B | SNARE_A | ')
  V3: REPEAT(8, `HAT_B ') REPEAT(8, `HAT_O ')
  
  V1: @mp REPEAT(2, `KICK_C | KICK_B | KICK_C | KICK_B | ')
  V2: REPEAT(8, `SNARE_A ')
  V3: REPEAT(8, `HAT_B ')
  
  V1: REPEAT(2, `KICK_A | KICK_A | KICK_A | KICK_A | ')
  V1: @diminuendo KICK_A | KICK_A | KICK_C FILL_END |
  V2: REPEAT(6, `SNARE_A ') r/2 r/4 snare/8 hat/16 kick/16 r/8 r/2 r/4 snare/8 hat/16 kick/16 r/8 |
  V2: @diminuendo SNARE_A | SNARE_A | r/1 |
  V3: REPEAT(8, `HAT_A ')

# ==============================
# Melody - Soft, spacey synth lead
# ==============================
lead_1_square: (tempo! 70) (time 4 4) (key c 'major)
  V1: @p r/1 | r/1 | r/1 | r/1 |
  V1: REPEAT(20, `r/1 | ')
  
  V1: @mp MELODY_A | r/2 MELODY_B | MELODY_C | MELODY_D |
  V1: MELODY_A | MELODY_B | r/1 | r/2 MELODY_C |
  
  V1: @mp r/4 MELODY_A | r/1 | r/2 MELODY_C | MELODY_D |
  V1: MELODY_B | r/2 MELODY_A | r/1 | r/1 |
  
  V1: @diminuendo r/1 | r/2 MELODY_A | r/1 | r/1 |
  V1: r/2 MELODY_C | r/1 | r/1 | r/1
