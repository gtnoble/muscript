# Lo-Fi Nightwalk (fixed for current parser/semantics)
# Generate: m4 examples/lofi_nightwalk.mus.m4 > examples/lofi_nightwalk.mus

define(`REPEAT', `ifelse($1, `0', `', `$2`'REPEAT(decr($1), `$2')')')dnl
define(`REPEAT_MEASURE', `ifelse($1, `0', `', `ifelse($1, `1', `$2', `$2 | REPEAT_MEASURE(decr($1), `$2')')')')dnl

define(`H1', `f3,a3,c4,e4/2 g3,b3-,d4,f4/2')dnl
define(`H2', `e3-,g3,b3-,d4/2 a2-,c3,e3-,g3/2')dnl

define(`B1', `f1/2 c2/2')dnl
define(`B2', `g1/2 d2/2')dnl
define(`B3', `e1-/2 b1-/2')dnl
define(`B4', `a1-/2 e2-/2')dnl

define(`K1', `kick/8 r/8 r/8 kick/8 r/8 kick/8 r/8 r/8')dnl
define(`K2', `kick/8 r/8 kick/8 r/8 r/8 kick/8 r/8 kick/8')dnl
define(`S1', `r/4 snare/8 r/8 r/4 snare/8 r/8')dnl
define(`HAT1', `hat/8 hat/8 hat/8 hat/8 hat/8 hat/8 hat/8 hat/8')dnl

define(`L1', `r/2 c5/8 e5-/8 g5/8 e5-/8')dnl
define(`L2', `r/2 b4-/8 d5/8 f5/8 d5/8')dnl
define(`L3', `r/1')dnl
define(`L4', `a4-/4 g4/8 f4/8 e4-/4 r/4')dnl

(tempo! 84);
(time 4 4);
(key f 'minor);
electric_piano_1 {
  V1: @mp :legato REPEAT_MEASURE(2, `H1 | H2 | H1 | H2');
  V1: @mf REPEAT_MEASURE(2, `H2 | H1 | H2 | H1');
}

(tempo! 84);
(time 4 4);
(key f 'minor);
bass {
  V1: @mp REPEAT_MEASURE(4, `B1 | B2 | B3 | B4');
}

(tempo! 84);
(time 4 4);
drums {
  V1: @mp REPEAT_MEASURE(8, `K1') | REPEAT_MEASURE(8, `K2');
  V2: @mp REPEAT_MEASURE(16, `S1');
  V3: @p REPEAT_MEASURE(16, `HAT1');
}

(tempo! 84);
(time 4 4);
(key f 'minor);
lead_1_square {
  V1: @p :legato REPEAT_MEASURE(2, `L3 | L3 | L1 | L2 | L3 | L4 | L1 | L2');
}
