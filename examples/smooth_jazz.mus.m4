# Smooth Jazz - Macro Source
# Tenor sax lead, Rhodes comping, electric bass, warm pad, and drums
# Generate with: m4 examples/smooth_jazz.mus.m4 > examples/smooth_jazz.mus

define(`REPEAT', `ifelse($1, `0', `', `$2`'REPEAT(decr($1), `$2')')')dnl
define(`REPEAT_MEASURE', `ifelse($1, `0', `', `ifelse($1, `1', `$2', `$2 | REPEAT_MEASURE(decr($1), `$2')')')')dnl

# ------------------------------
# Jazzy chord voicings (2-bar / 1-bar snippets)
# Key: F major center
# ------------------------------
define(`CHORD_A1', `a3,c4,e4,g4/4. r/8 a3,c4,e4,g4/8 r/8 r/4')dnl
define(`CHORD_A2', `f3,a3,c4,e4/4. r/8 f3,a3,c4,e4/8 r/8 r/4')dnl

define(`CHORD_B1', `g3,b3-,d4,f4/4. r/8 g3,b3-,d4,f4/8 r/8 r/4')dnl
define(`CHORD_B2', `a3,c4,e4,g4/4. r/8 a3,c4,e4,g4/8 r/8 r/4')dnl

define(`CHORD_C1', `b3-,d4,f4,a4/4. r/8 b3-,d4,f4,a4/8 r/8 r/4')dnl
define(`CHORD_C2', `c4,e4,g4,b4-/4. r/8 c4,e4,g4,b4-/8 r/8 r/4')dnl

define(`CHORD_D1', `d3,f3,a3,c4/4. r/8 d3,f3,a3,c4/8 r/8 r/4')dnl
define(`CHORD_D2', `g3,b3,d4,f4/4. r/8 g3,b3,d4,f4/8 r/8 r/4')dnl

# ------------------------------
# Bass snippets (smooth fingered patterns)
# ------------------------------
define(`BASS_F', `f2/2 a2/4 r/4')dnl
define(`BASS_Gm', `g2/2 b2-/4 r/4')dnl
define(`BASS_Am', `a2/2 c3/4 r/4')dnl
define(`BASS_Bb', `b2-/2 d3/4 r/4')dnl
define(`BASS_C', `c3/2 e3/4 r/4')dnl
define(`BASS_Dm', `d2/2 f2/4 r/4')dnl

# ------------------------------
# Drum patterns (ride, snare brushes, soft kick)
# ------------------------------
define(`KICK_J', `kick/4 r/4 kick/4 r/4')dnl
define(`SNARE_J', `r/4 snare/4 r/4 snare/4')dnl
define(`RIDE_J', `ride/8 ride/8 ride/8 ride/8 ride/8 ride/8 ride/8 ride/8')dnl
define(`FILL_SHORT', `kick/8 snare/8 hat/8 tom1/8 r/2')dnl

# ------------------------------
# Lead fragments for tenor sax (2-bar phrases)
# ------------------------------
define(`MELODY_1', `a4/4 c5/8 e5/8 r/2')dnl
define(`MELODY_2', `d5/4 c5/4 r/2')dnl
define(`MELODY_3', `g4/4 a4/8 c5/8 r/2')dnl
define(`MELODY_4', `f4/2 e4/4 d4/4')dnl

# ------------------------------
# Global directives and arrangement
# A = 16 bars, B = 16 bars (bridge), repeat structure to make 64 bars
# ------------------------------
(tempo! 100);
(time 4 4);
(key f 'major);

electric_piano_1 {
  V1: @mp :legato REPEAT_MEASURE(4, `CHORD_A1 | CHORD_A2 | CHORD_B1 | CHORD_B2');
  V1: @mf REPEAT_MEASURE(4, `CHORD_C1 | CHORD_C2 | CHORD_D1 | CHORD_D2');
  V1: @mp REPEAT_MEASURE(4, `CHORD_A1 | CHORD_A2 | CHORD_B1 | CHORD_B2');
  V1: @mf REPEAT_MEASURE(4, `CHORD_C1 | CHORD_C2 | CHORD_D1 | CHORD_D2');
}

pad_2_warm {
  V1: @p REPEAT_MEASURE(16, `CHORD_A1 | CHORD_A1 | CHORD_A1 | CHORD_A1');
  V1: @p REPEAT_MEASURE(16, `CHORD_C1 | CHORD_C1 | CHORD_C1 | CHORD_C1');
}

bass {
  V1: @mf REPEAT_MEASURE(4, `BASS_F | BASS_Gm | BASS_Am | BASS_Bb');
  V1: @mf REPEAT_MEASURE(4, `BASS_C | BASS_Dm | BASS_Gm | BASS_F');
  V1: @mf REPEAT_MEASURE(4, `BASS_F | BASS_Gm | BASS_Am | BASS_Bb');
  V1: @mf REPEAT_MEASURE(4, `BASS_C | BASS_Dm | BASS_Gm | BASS_F');
}

drums {
  V1: @mp REPEAT_MEASURE(8, `KICK_J | KICK_J');
  V2: REPEAT_MEASURE(16, `SNARE_J');
  V3: REPEAT_MEASURE(32, `RIDE_J');

  V1: @mf REPEAT_MEASURE(4, `KICK_J | FILL_SHORT | KICK_J | KICK_J');
  V2: REPEAT_MEASURE(4, `SNARE_J | SNARE_J | SNARE_J | SNARE_J');
  V3: REPEAT_MEASURE(4, `RIDE_J | RIDE_J | RIDE_J | RIDE_J');

  V1: @diminuendo REPEAT_MEASURE(2, `KICK_J | KICK_J');
  V2: REPEAT_MEASURE(4, `SNARE_J');
  V3: REPEAT_MEASURE(4, `RIDE_J');
}

tenor_sax {
  V1: @mp REPEAT_MEASURE(8, `r/1');
  V1: @mf MELODY_1 | MELODY_2 | MELODY_3 | MELODY_4;
  V1: @mf REPEAT_MEASURE(4, `MELODY_1 | MELODY_2');
  V1: @mp REPEAT_MEASURE(4, `MELODY_3 | MELODY_4');
  V1: @diminuendo REPEAT_MEASURE(4, `r/1');
}

# End - a gentle tag
electric_piano_1 {
  V1: @p CHORD_A1 | CHORD_A2 | CHORD_A1 | CHORD_A2; 
}