# Drum Beat Demo (Macro Source)
# Generate: m4 examples/drum_beat.mus.m4 > examples/drum_beat.mus

define(`REPEAT', `ifelse($1, `0', `', `$2`'REPEAT(decr($1), `$2')')')dnl

define(`ROCK_KICK', `kick/8 r/8 r/8 r/8 kick/8 r/8 r/8 r/8')dnl
define(`ROCK_SNARE', `r/8 r/8 r/8 snare/8 r/8 r/8 r/8 snare/8')dnl
define(`ROCK_HAT', `hat/8 hat/8 hat/8 hat/8 hat/8 hat/8 hat/8 hat/8')dnl

define(`FLOOR_KICK', `kick/4 kick/4 kick/4 kick/4')dnl
define(`FLOOR_SNARE', `r/4 snare/4 r/4 snare/4')dnl

define(`BREAK_KICK', `kick/16 r/16 r/16 kick/16 r/16 r/16 r/16 r/16 kick/16 r/16 r/16 r/16 kick/16 r/16 r/16 r/16')dnl
define(`BREAK_SNARE', `r/16 r/16 r/16 r/16 snare/16 r/16 snare/16 r/16 r/16 snare/16 r/16 r/16 snare/16 r/16 snare/16 snare/16')dnl
define(`BREAK_HAT', `hat/8 hat/8 openhat/8 hat/8 hat/8 hat/8 openhat/8 hat/8')dnl

# Section 1: Basic Rock Beat
# Classic kick on 1 and 3, snare on 2 and 4, hi-hat eighths
(tempo! 120) (time 4 4)
drums {
  V1: REPEAT(4, `ROCK_KICK | ')
  V2: REPEAT(4, `ROCK_SNARE | ')
  V3: REPEAT(4, `ROCK_HAT | ')
}

# Section 2: Four-on-the-Floor (Disco/House)
drums {
  V1: REPEAT(4, `FLOOR_KICK | ')
  V2: REPEAT(4, `FLOOR_SNARE | ')
  V3: REPEAT(4, `ROCK_HAT | ')
}

# Section 3: Funk Pattern with Ghost Notes
drums {
  V1: REPEAT(2, `BREAK_KICK | ')
  V2: @mf REPEAT(2, `BREAK_SNARE | ')
  V3: :staccato REPEAT(16, `hat/16 ') |
}

# Section 4: Drum Fill with Toms
drums {
  V1: @f tom1/8 tom1/8 tom2/8 tom2/8 tom3/8 tom3/8 tom4/8 tom4/8 |
  V1: @ff crash/2 kick/4 snare/4 |
}
