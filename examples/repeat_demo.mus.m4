# Macro Source Demo (.mus.m4)
# Generate: m4 examples/repeat_demo.mus.m4 > examples/repeat_demo.mus

define(`REPEAT', `ifelse($1, `0', `', `$2`'REPEAT(decr($1), `$2')')')dnl

define(`PIANO_BAR', `c4/4 d4/4 e4/4 f4/4')dnl
define(`BASS_BAR', `c3/2 g3/2')dnl
define(`FLUTE_BAR', `c5/4 d5/4 e5/4 f5/4')dnl

define(`ROCK_KICK', `kick/8 r/8 r/8 r/8 kick/8 r/8 r/8 r/8')dnl
define(`ROCK_SNARE', `r/8 r/8 r/8 snare/8 r/8 r/8 r/8 snare/8')dnl
define(`ROCK_HAT', `hat/8 hat/8 hat/8 hat/8 hat/8 hat/8 hat/8 hat/8')dnl

REPEAT(2, 
`
(tempo! 120);
(time 4 4);
piano {
  V1: PIANO_BAR;
  V2: BASS_BAR;
}

drums {
  V1: ROCK_KICK;
  V2: ROCK_SNARE;
  V3: ROCK_HAT;
}

flute {
  V1: FLUTE_BAR;
}
')