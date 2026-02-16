# Smooth Jazz (rewrite from scratch)
# 56 bars: Intro 8 + A1 16 + A2 16 + Bridge 8 + Outro 8
# Generate: m4 examples/smooth_jazz.mus.m4 > examples/smooth_jazz.mus

define(`REPEAT', `ifelse($1, `0', `', `$2`'REPEAT(decr($1), `$2')')')dnl

# ==============================
# Harmony (8-bar loop, D minor)
# Dm9 | Gm9 | C13 | Fmaj9 | Bbmaj9 | Em7b5 A7(b9) | Dm9 | A7sus
# ==============================

define(`CH_Dm9',  `f3/8,a3/8,c4/8,e4/8')dnl
define(`CH_Gm9',  `b2-/8,d3/8,f3/8,a3/8')dnl
define(`CH_C13',  `e3/8,a3/8,b3-/8,d4/8')dnl
define(`CH_Fmaj9',`a2/8,c3/8,e3/8,g3/8')dnl
define(`CH_Bbmaj9',`d3/8,f3/8,a3/8,c4/8')dnl
define(`CH_Em7b5',`g3/8,b3-/8,d4/8,f4/8')dnl
define(`CH_A7b9', `c4+/8,e4/8,g4/8,b3-/8')dnl
define(`CH_A7sus',`d4/8,e4/8,g4/8,a3/8')dnl

# Comp patterns (each = one 4/4 bar in eighth grid)
define(`COMP1', `r/8 $1 r/4 $1 r/8 r/8 $1')dnl
define(`COMP2', `$1 r/8 r/8 $1 r/4 $1 r/8')dnl
define(`COMP3', `r/8 $1 r/8 $1 r/8 $1 r/8 $1')dnl

define(`BAR1_Dm9',   `COMP1(CH_Dm9)')dnl
define(`BAR2_Gm9',   `COMP2(CH_Gm9)')dnl
define(`BAR3_C13',   `COMP1(CH_C13)')dnl
define(`BAR4_Fmaj9', `COMP2(CH_Fmaj9)')dnl
define(`BAR5_Bbmaj9',`COMP1(CH_Bbmaj9)')dnl
define(`BAR6_EmA',   `r/8 CH_Em7b5 r/8 CH_Em7b5 r/8 CH_A7b9 r/8 CH_A7b9')dnl
define(`BAR7_Dm9',   `COMP3(CH_Dm9)')dnl
define(`BAR8_A7sus', `COMP2(CH_A7sus)')dnl

define(`COMP_LOOP_A', `BAR1_Dm9 | BAR2_Gm9 | BAR3_C13 | BAR4_Fmaj9 | BAR5_Bbmaj9 | BAR6_EmA | BAR7_Dm9 | BAR8_A7sus |')dnl

# ==============================
# Bass (walking eighths)
# ==============================

define(`B_Dm9',  `d2/8 f2/8 a2/8 c3/8 e3/8 d3/8 c3/8 a2/8')dnl
define(`B_Gm9',  `g1/8 b1-/8 d2/8 f2/8 a2/8 g2/8 f2/8 d2/8')dnl
define(`B_C13',  `c2/8 e2/8 g2/8 b2-/8 d3/8 c3/8 b2-/8 g2/8')dnl
define(`B_Fmaj9',`f1/8 a1/8 c2/8 e2/8 g2/8 f2/8 e2/8 c2/8')dnl
define(`B_Bbmaj9',`b1-/8 d2/8 f2/8 a2/8 c3/8 b2-/8 a2/8 f2/8')dnl
define(`B_EmA',  `e2/8 g2/8 b2-/8 d3/8 a1/8 c2+/8 e2/8 g2/8')dnl
define(`B_A7sus',`a1/8 d2/8 e2/8 g2/8 a2/8 g2/8 e2/8 d2/8')dnl

define(`BASS_LOOP_A', `B_Dm9 | B_Gm9 | B_C13 | B_Fmaj9 | B_Bbmaj9 | B_EmA | B_Dm9 | B_A7sus |')dnl

# ==============================
# Drums (swing ride + light backbeat)
# ==============================

define(`RIDE_SW', `ride/8. ride/16 ride/8. ride/16 ride/8. ride/16 ride/8. ride/16')dnl
define(`HAT_SW',  `hat/8. hat/16 hat/8. hat/16 hat/8. hat/16 hat/8. hat/16')dnl
define(`HAT_SW_O',`hat/8. hat/16 hat/8. hat/16 hat/8. hat/16 openhat/8. hat/16')dnl

define(`SN_BACK', `r/4 rimshot/8 r/8 r/4 snare/8 r/8')dnl
define(`SN_GHOST',`r/8 snare/16 r/16 rimshot/8 r/8 r/8 snare/16 r/16 rimshot/8 r/8')dnl

define(`KICK_A',  `kick/8 r/8 r/8 kick/8 r/8 kick/8 r/8 kick/8')dnl
define(`KICK_B',  `kick/8 r/8 kick/8 r/8 r/8 kick/8 r/8 kick/8')dnl
define(`KICK_FILL',`tom2/16 tom3/16 tom4/16 tom3/16 tom2/16 tom1/16 snare/16 r/16 crash/8 kick/8 r/8 r/8')dnl

# ==============================
# Composition
# ==============================

(tempo! 96) (time 4 4) (key d 'minor) (pan 48)
electric_piano_1 {
  # Intro (8)
  V1: @mp :legato REPEAT(1, `COMP_LOOP_A')
  V1: @mp :tenuto REPEAT(1, `COMP_LOOP_A')

  # A1 (16)
  V1: @mf :tenuto REPEAT(2, `COMP_LOOP_A')

  # A2 (16)
  V1: @mf :legato REPEAT(2, `COMP_LOOP_A')

  # Bridge (8)
  V1: @mp REPEAT(1, `COMP_LOOP_A')

  # Outro (8)
  V1: @mf BAR1_Dm9 | BAR2_Gm9 | BAR3_C13 | BAR4_Fmaj9 | BAR5_Bbmaj9 | BAR6_EmA | BAR7_Dm9 |
  V1: @diminuendo BAR8_A7sus |
  V1: @p d3/1,f3/1,a3/1,c4/1 |
}

(tempo! 96) (time 4 4) (key d 'minor) (pan 64)
bass {
  # Intro (8)
  V1: @mp r/1 | r/1 | r/1 | r/1 |
  V1: REPEAT(1, `BASS_LOOP_A')

  # A1 (16)
  V1: @mf REPEAT(2, `BASS_LOOP_A')

  # A2 (16)
  V1: @mf REPEAT(2, `BASS_LOOP_A')

  # Bridge (8)
  V1: @mp REPEAT(1, `BASS_LOOP_A')

  # Outro (8)
  V1: @mf B_Dm9 | B_Gm9 | B_C13 | B_Fmaj9 | B_Bbmaj9 | B_EmA | B_Dm9 | @diminuendo B_A7sus |
  V1: @p d2/1 |
}

(tempo! 96) (time 4 4)
drums {
  # Intro (8) — brushes-ish (hat only), then groove
  V1: @p r/1 | r/1 | r/1 | r/1 |
  V1: @mp REPEAT(4, `KICK_A ')
  V2: @p r/1 | r/1 | r/1 | r/1 |
  V2: @mp REPEAT(4, `SN_BACK ')
  V3: @p REPEAT(4, `HAT_SW ')
  V3: @mp REPEAT(3, `HAT_SW ') HAT_SW_O

  # A1 (16)
  V1: @mp REPEAT(8, `KICK_A ') REPEAT(8, `KICK_B ')
  V2: @mp REPEAT(8, `SN_BACK ') REPEAT(8, `SN_GHOST ')
  V3: @mp REPEAT(15, `RIDE_SW ') RIDE_SW

  # A2 (16)
  V1: @mf REPEAT(15, `KICK_B ') KICK_FILL
  V2: @mf REPEAT(16, `SN_GHOST ')
  V3: @mf REPEAT(16, `RIDE_SW ')

  # Bridge (8)
  V1: @mp REPEAT(8, `KICK_A ')
  V2: @mp REPEAT(8, `SN_BACK ')
  V3: @mp REPEAT(8, `RIDE_SW ')

  # Outro (8)
  V1: @mf REPEAT(7, `KICK_A ') KICK_FILL
  V2: @mf REPEAT(8, `SN_BACK ')
  V3: @diminuendo REPEAT(7, `HAT_SW ') r/1
}
