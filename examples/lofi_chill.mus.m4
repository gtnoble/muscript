# Lo-Fi Chill Beat
# Better structured lofi with neo-soul chord progressions
# Generate: m4 examples/lofi_chill.mus.m4 > examples/lofi_chill.mus

define(`REPEAT', `ifelse($1, `0', `', `$2`'REPEAT(decr($1), `$2')')')dnl
define(`REPEAT_MEASURE', `ifelse($1, `0', `', `ifelse($1, `1', `$2', `$2 | REPEAT_MEASURE(decr($1), `$2')')')')dnl

# ==============================
# Neo-Soul Rhodes Chords
# More interesting voicings and variations
# ==============================

# A Section: Fmaj7 - G7 - Em7 - Am7 (vi-VII-v-i in A minor)
define(`CHORD_A1', `f3/4,a3/4,c4/4,e4/4 r/8 a3/8,c4/8,e4/8 r/4 f3/4,a3/4,e4/4')dnl
define(`CHORD_A2', `g3/4,b3/4,d4/4,f4/4 r/8 b3/8,d4/8,f4/8 r/4 g3/4,d4/4,f4/4')dnl
define(`CHORD_A3', `e3/4,g3/4,b3/4,d4/4 r/8 g3/8,b3/8,d4/8 r/4 e3/4,b3/4,d4/4')dnl
define(`CHORD_A4', `a2/4,c3/4,e3/4,g3/4 r/8 c3/8,e3/8,g3/8 r/4 a2/4,e3/4,g3/4')dnl

# B Section: Dm7 - G7 - Cmaj7 - Fmaj7 (ii-V-I-IV progression)
define(`CHORD_B1', `d3/4,f3/4,a3/4,c4/4 r/8 f3/8,a3/8,c4/8 r/4 d3/4,a3/4,c4/4')dnl
define(`CHORD_B2', `g3/4,b3/4,d4/4,f4/4 r/8 b3/8,d4/8,f4/8 r/4 g3/4,b3/4,f4/8')dnl
define(`CHORD_B3', `c3/4,e3/4,g3/4,b3/4 r/8 e3/8,g3/8,b3/8 r/4 c3/4,g3/4,b3/4')dnl
define(`CHORD_B4', `f3/4,a3/4,c4/4,e4/4 r/8 a3/8,c4/8,e4/8 r/4 f3/4,c4/4,e4/4')dnl

# C Section: Am7 - Dm7 - G7 - Cmaj7 (Bridge/Turnaround)
define(`CHORD_C1', `a2/4,c3/4,e3/4,g3/4 r/8 c3/8,e3/8,g3/8 r/4 a2/4,e3/4,g3/4')dnl
define(`CHORD_C2', `d3/4,f3/4,a3/4,c4/4 r/8 f3/8,a3/8,c4/8 r/4 d3/4,a3/4,c4/4')dnl
define(`CHORD_C3', `g3/4,b3/4,d4/4,f4/4 r/8 b3/8,d4/8,f4/8 r/4 g3/4,d4/4,f4/4')dnl
define(`CHORD_C4', `c3/4,e3/4,g3/4,b3/4 r/8 e3/8,g3/8,b3/8 r/4 c3/4,g3/4,b3/4')dnl

# ==============================
# Bass Lines (Walking bass style)
# ==============================
define(`BASS_A', `f2/4 r/8 f2/8 r/2 | g2/4 r/8 g2/8 r/2 | e2/4 r/8 e2/8 r/2 | a1/4 r/8 a1/8 r/2')dnl
define(`BASS_B', `d2/4 r/8 d2/8 r/2 | g2/4 r/8 g2/8 r/2 | c2/4 r/8 c2/8 r/2 | f2/4 r/8 f2/8 r/2')dnl
define(`BASS_C', `a1/4 r/8 c2/8 r/2 | d2/4 r/8 f2/8 r/2 | g2/4 r/8 b2/8 r/2 | c2/4 r/8 e2/8 r/2')dnl

# ==============================
# Boom-Bap Drum Patterns
# ==============================
define(`KICK_1', `kick/8 r/16 r/16 r/8 kick/16 r/16 r/4 kick/8 r/8')dnl
define(`KICK_2', `kick/8 r/16 r/16 r/8 kick/16 r/16 r/8 r/16 kick/16 r/8 r/8')dnl
define(`KICK_3', `kick/8 r/8 r/8 kick/8 kick/16 r/16 r/8 kick/8 r/8')dnl

define(`SNARE_1', `r/4 snare/8 r/8 r/4 snare/8 r/16 r/16')dnl
define(`SNARE_2', `r/4 snare/8 r/16 snare/16 r/4 snare/8 r/8')dnl

define(`HAT_1', `hat/16 r/16 hat/16 r/16 hat/16 r/16 hat/16 r/16 hat/16 r/16 hat/16 r/16 hat/16 r/16 hat/16 r/16')dnl
define(`HAT_2', `hat/16 r/16 hat/16 hat/16 r/16 hat/16 r/16 hat/16 hat/16 r/16 hat/16 r/16 hat/16 r/16 hat/16 r/16')dnl
define(`HAT_3', `hat/16 r/16 openhat/16 r/16 hat/16 r/16 hat/16 r/16 hat/16 r/16 hat/16 r/16 openhat/16 r/16 hat/16 r/16')dnl

# ==============================
# Melodic Fragments
# Sparse, emotional phrases
# ==============================
define(`MELODY_1', `r/4 a4/16 c5/16 r/8 e5/8 d5/8 c5/16 a4/16 r/8')dnl
define(`MELODY_2', `r/2 c5/8 d5/8 e5/8 g5/8')dnl
define(`MELODY_3', `a5/8 r/8 g5/8 r/8 e5/4 d5/8 c5/8')dnl
define(`MELODY_4', `r/8 e5/8 d5/8 c5/8 a4/4 g4/8 a4/8')dnl
define(`MELODY_5', `g5/16 a5/16 g5/8 e5/8 d5/8 c5/8 r/4 r/8')dnl

# ==============================
# Main Composition
# ==============================

# Rhodes Piano
(tempo! 75);
(time 4 4);
(key a 'minor);
electric_piano_1 {
  # Intro (4 bars - build up)
  V1: @p :legato CHORD_A1 | CHORD_A2 | CHORD_A3 | CHORD_A4;
  
  # A Section (16 bars - main groove)
  V1: @mp :legato REPEAT_MEASURE(4, `CHORD_A1 | CHORD_A2 | CHORD_A3 | CHORD_A4');
  
  # B Section (8 bars - progression shift)
  V1: @mf CHORD_B1 | CHORD_B2 | CHORD_B3 | CHORD_B4;
  V1: CHORD_B1 | CHORD_B2 | CHORD_B3 | CHORD_B4;
  
  # A Section Return (8 bars)
  V1: @mp REPEAT_MEASURE(2, `CHORD_A1 | CHORD_A2 | CHORD_A3 | CHORD_A4');
  
  # C Section Bridge (8 bars)
  V1: @mf CHORD_C1 | CHORD_C2 | CHORD_C3 | CHORD_C4;
  V1: CHORD_C1 | CHORD_C2 | CHORD_C3 | CHORD_C4;
  
  # Outro (8 bars - fade feel)
  V1: @diminuendo @mp REPEAT_MEASURE(2, `CHORD_A1 | CHORD_A2 | CHORD_A3 | CHORD_A4');
}

# Bass
(tempo! 75);
(time 4 4);
(key a 'minor);
bass {
  V1: @mp r/1 | r/1 | r/1 | r/1;
  V1: @mp REPEAT_MEASURE(4, `BASS_A');
  V1: @mf REPEAT_MEASURE(2, `BASS_B');
  V1: @mp REPEAT_MEASURE(2, `BASS_A');
  V1: @mf REPEAT_MEASURE(2, `BASS_C');
  V1: @diminuendo @mp REPEAT_MEASURE(2, `BASS_A');
}

# Drums
(tempo! 75);
(time 4 4);
drums {
  # Intro - minimal drums
  V1: @p r/1 | r/1 | r/2 r/2 | KICK_1;
  V2: r/1 | r/1 | r/2 r/2 | SNARE_1;
  V3: r/1 | r/1 | r/2 r/2 | HAT_1;
  
  V1: @mp KICK_1;
  V2: SNARE_1;
  V3: HAT_1;
  
  # A Section Main Beat
  V1: @mp REPEAT_MEASURE(8, `KICK_1') | REPEAT_MEASURE(8, `KICK_2');
  V2: REPEAT_MEASURE(16, `SNARE_1');
  V3: REPEAT_MEASURE(8, `HAT_1') | REPEAT_MEASURE(4, `HAT_2') | REPEAT_MEASURE(4, `HAT_3');
  
  # B Section - more energetic
  V1: @mf REPEAT_MEASURE(4, `KICK_2') | REPEAT_MEASURE(4, `KICK_3');
  V2: REPEAT_MEASURE(4, `SNARE_1') | REPEAT_MEASURE(4, `SNARE_2');
  V3: REPEAT_MEASURE(8, `HAT_3');
  
  # A Return
  V1: @mp REPEAT_MEASURE(8, `KICK_1');
  V2: REPEAT_MEASURE(8, `SNARE_1');
  V3: REPEAT_MEASURE(8, `HAT_2');
  
  # C Section Bridge
  V1: @mf REPEAT_MEASURE(8, `KICK_2');
  V2: REPEAT_MEASURE(8, `SNARE_2');
  V3: REPEAT_MEASURE(8, `HAT_3');
  
  # Outro - with fill
  V1: @mp REPEAT_MEASURE(7, `KICK_1') | kick/8 r/8 r/4 kick/4 snare/8 tom1/16 tom2/16;
  V2: REPEAT_MEASURE(7, `SNARE_1') | r/2 r/4 snare/8 r/8;
  V3: @diminuendo REPEAT_MEASURE(8, `HAT_1');
}

# Lead Melody - Soft Square Wave or Bell-like
(tempo! 75);
(time 4 4);
(key a 'minor);
lead_1_square {
  V1: @pp r/1 | r/1 | r/1 | r/1;
  V1: REPEAT_MEASURE(8, `r/1');
  V1: REPEAT_MEASURE(8, `r/1');
  
  # Enter in B section
  V1: @p :legato MELODY_1 | MELODY_2 | MELODY_3 | MELODY_4;
  V1: MELODY_5 | MELODY_1 | MELODY_2 | r/1;
  
  # Sparse in A return
  V1: @pp r/1 | r/1 | MELODY_3 | r/1;
  V1: r/1 | MELODY_5 | r/1 | r/1;
  
  # More active in C bridge
  V1: @mp MELODY_1 | MELODY_2 | MELODY_4 | MELODY_3;
  V1: MELODY_5 | MELODY_1 | MELODY_2 | r/1;
  
  # Fade in outro
  V1: @diminuendo r/1 | MELODY_4 | r/1 | MELODY_5;
  V1: @pp r/1 | MELODY_3 | r/1 | r/1;
}
