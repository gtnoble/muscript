# Lo-Fi Nightwalk (Macro Source)
# Original composition: dusty boom-bap + neo-soul minor chords
# Generate: m4 examples/lofi_nightwalk.mus.m4 > examples/lofi_nightwalk.mus

define(`REPEAT', `ifelse($1, `0', `', `$2`'REPEAT(decr($1), `$2')')')dnl

# ==============================
# Harmony (1 bar each)
# Key center: F minor (natural minor / dorian-ish color)
# Rhythm: dotted-quarter hit, pickup hit, backbeat hit
# Bar total = /4. + r/8 + /8 + r/8 + /4
# ==============================

define(`CH_FM9',  `f3/4.,a3/4.,c4/4.,e4/4.,g4/4. r/8 f3/8,a3/8,c4/8,e4/8,g4/8 r/8 f3/4,a3/4,c4/4,e4/4,g4/4')dnl
define(`CH_BBM9', `b2/4.,d3/4.,f3/4.,a3/4.,c4/4. r/8 b2/8,d3/8,f3/8,a3/8,c4/8 r/8 b2/4,d3/4,f3/4,a3/4,c4/4')dnl
define(`CH_EB13', `e3/4.,g3/4.,b3/4.,d4/4.,f4/4.,c5/4. r/8 e3/8,g3/8,b3/8,d4/8,f4/8 r/8 e3/4,g3/4,b3/4,d4/4,f4/4')dnl
define(`CH_ABM9', `a2/4.,c3/4.,e3/4.,g3/4.,b3/4. r/8 a2/8,c3/8,e3/8,g3/8,b3/8 r/8 a2/4,c3/4,e3/4,g3/4,b3/4')dnl

define(`CH_DBM9', `d3/4.,f3/4.,a3/4.,c4/4.,e4/4. r/8 d3/8,f3/8,a3/8,c4/8,e4/8 r/8 d3/4,f3/4,a3/4,c4/4,e4/4')dnl
# C7(b9) in F minor key: e3+ is E natural, d4 is Db due to key signature
define(`CH_C7B9', `c3/4.,e3+/4.,g3/4.,b3/4.,d4/4. r/8 c3/8,e3+/8,g3/8,b3/8,d4/8 r/8 c3/4,e3+/4,g3/4,b3/4')dnl

# Slight variation for longer sections (more air)
define(`CH_AIR_FM9',  `f3/4.,a3/4.,c4/4.,e4/4.,g4/4. r/4 f3/8,a3/8,c4/8,e4/8,g4/8 r/8 f3/8,a3/8,c4/8,e4/8,g4/8')dnl

define(`PROG_A', `CH_FM9 | CH_BBM9 | CH_EB13 | CH_ABM9 | ')dnl
define(`PROG_B', `CH_DBM9 | CH_C7B9 | CH_FM9 | CH_ABM9 | ')dnl

# ==============================
# Bass (1 bar each)
# Syncopated 16th pickups, stays inside 4/4
# ==============================

define(`BS_F',  `f1/8 r/16 f1/16 c2/8 r/8 e2/8 r/16 e2/16 f2/8 r/8')dnl
define(`BS_BB', `b1/8 r/16 b1/16 f2/8 r/8 a2/8 r/16 a2/16 b2/8 r/8')dnl
define(`BS_EB', `e2/8 r/16 e2/16 b2/8 r/8 d3/8 r/16 d3/16 e3/8 r/8')dnl
define(`BS_AB', `a1/8 r/16 a1/16 e2/8 r/8 g2/8 r/16 g2/16 a2/8 r/8')dnl

define(`BS_DB', `d2/8 r/16 d2/16 a2/8 r/8 c3/8 r/16 c3/16 d3/8 r/8')dnl
define(`BS_C',  `c2/8 r/16 c2/16 g2/8 r/8 b2/8 r/16 b2/16 c3/8 r/8')dnl

define(`BPROG_A', `BS_F | BS_BB | BS_EB | BS_AB | ')dnl
define(`BPROG_B', `BS_DB | BS_C | BS_F | BS_AB | ')dnl

# ==============================
# Drums (1 bar each)
# V1 kick, V2 snare(+ghost), V3 hats
# ==============================

define(`K_A', `kick/8 r/8 r/16 kick/16 r/8 r/8 kick/16 r/16 r/8 kick/16 r/16 r/8')dnl
define(`K_B', `kick/8 r/16 kick/16 r/8 r/8 kick/16 r/16 r/8 kick/16 r/16 r/8 kick/8')dnl

define(`S_A', `r/4 snare/8 r/16 snare/16 r/4 snare/8 r/8')dnl
define(`S_B', `r/4 snare/8 r/8 r/8 snare/16 r/16 snare/8 r/8')dnl

define(`H_16', `hat/16 r/16 hat/16 r/16 hat/16 r/16 hat/16 r/16 hat/16 r/16 hat/16 r/16 hat/16 r/16 hat/16 r/16')dnl
define(`H_SOLID', `hat/16 hat/16 hat/16 hat/16 hat/16 hat/16 hat/16 hat/16 hat/16 hat/16 hat/16 hat/16 hat/16 hat/16 hat/16 hat/16')dnl
define(`H_PUSH', `hat/16 r/16 hat/16 hat/16 r/16 hat/16 r/16 hat/16 hat/16 r/16 hat/16 r/16 hat/16 r/16 hat/16 r/16')dnl
define(`H_OPEN', `hat/16 r/16 hat/16 r/16 hat/16 r/16 hat/16 r/16 hat/16 r/16 hat/16 r/16 openhat/16 r/16 hat/16 r/16')dnl

define(`CRASH_1', `crash/4 r/4 r/2')dnl
define(`RIDE_8', `ride/8 ride/8 ride/8 ride/8 ride/8 ride/8 ride/8 ride/8')dnl

define(`FILL', `kick/8 r/8 kick/16 tom1/16 tom2/16 tom1/16 snare/8 r/8 kick/8 snare/8 tom2/16 tom1/16')dnl

# ==============================
# Lead motifs (1 bar each)
# Sparse bell/square phrases (pentatonic-ish)
# ==============================

define(`LD_1', `r/2 c5/16 e5/16 g5/8 r/8 f5/8 e5/16 c5/16 r/8')dnl
define(`LD_2', `r/4 a4/16 c5/16 r/8 e5/8 r/8 d5/8 c5/16 a4/16 r/4')dnl
define(`LD_3', `r/2 r/8 g5/8 a5/8 c6/8 g5/4 r/8')dnl
define(`LD_4', `r/4 r/8 e5/16 f5/16 e5/8 c5/8 a4/8 g4/8 r/8 r/8')dnl

# ==============================
# Composition
# 4 intro + 16 main + 8 bridge + 4 outro = 32 bars
# ==============================

electric_piano_1: (tempo! 84) (time 4 4) (key f 'minor)
  # Intro (4) - airy comp
  V1: @mf :legato CH_AIR_FM9 | CH_AIR_FM9 | CH_FM9 | CH_BBM9 |
  V2: @mp r/1 | r/1 | f2/1 | b1/1 |

  # Main (16) - steady progression
  V1: @f :tenuto REPEAT(4, `PROG_A')
  V2: @mf REPEAT(4, `f2/1 | b1/1 | e2/1 | a1/1 | ')

  # Bridge (8) - turnaround color
  V1: @f REPEAT(2, `PROG_B')
  V2: @mf REPEAT(2, `d2/1 | c2/1 | f2/1 | a1/1 | ')

  # Outro (4) - fade
  V1: @diminuendo @mf CH_AIR_FM9 | CH_FM9 | CH_BBM9 | f3/1,a3/1,c4/1,e4/1,g4/1 |
  V2: @diminuendo @mp f2/1 | b1/1 | f2/1 | f2/1 |

bass: (tempo! 84) (time 4 4) (key f 'minor)
  # Intro (4) - enter late
  V1: @mp r/1 | r/1 | BS_F | BS_BB |

  # Main (16)
  V1: @f REPEAT(4, `BPROG_A')

  # Bridge (8)
  V1: @f REPEAT(2, `BPROG_B')

  # Outro (4)
  V1: @diminuendo @mp BS_F | BS_BB | BS_F | f1/1 |

# Dusty boom-bap kit
# V1 kick, V2 snare, V3 hats

drums: (tempo! 84) (time 4 4)
  # Intro (4) - hats first, snare enters bar 3
  V1: @p r/1 | r/1 | K_A | K_A |
  V2: r/1 | r/1 | S_A | S_A |
  V3: H_16 | H_16 | H_PUSH | H_PUSH |
  V4: r/1 | r/1 | CRASH_1 | r/1 |

  # Main (16)
  V1: @mf REPEAT(8, `K_A | ') REPEAT(8, `K_B | ')
  V2: REPEAT(8, `S_A | ') REPEAT(8, `S_B | ')
  V3: REPEAT(8, `H_16 | ') REPEAT(4, `H_SOLID | ') REPEAT(4, `H_OPEN | ')
  V4: REPEAT(4, `CRASH_1 | r/1 | r/1 | r/1 | ')

  # Bridge (8) - open hats + slightly busier kick
  V1: @f REPEAT(7, `K_B | ') FILL |
  V2: @mf REPEAT(8, `S_B | ')
  V3: @mf REPEAT(4, `H_OPEN | ') REPEAT(4, `RIDE_8 | ')
  V4: CRASH_1 | r/1 | r/1 | r/1 | CRASH_1 | r/1 | r/1 | r/1 |

  # Outro (4)
  V1: @mf K_A | K_A | r/2 kick/8 r/8 | r/1 |
  V2: S_A | S_A | r/2 snare/8 r/8 | r/1 |
  V3: @diminuendo H_16 | H_16 | H_PUSH | r/1 |
  V4: CRASH_1 | r/1 | r/1 | r/1 |

# Bell-like lead; keep it sparse and late
lead_1_square: (tempo! 84) (time 4 4) (key f 'minor)
  # 32 bars total: 4 intro rest + 16 main + 8 bridge + 4 outro
  V1: @pp REPEAT(4, `r/1 | ')
  V1: @p :legato REPEAT(2, `LD_1 | LD_2 | LD_3 | LD_4 | ')
  V1: @mp REPEAT(2, `LD_2 | LD_1 | LD_3 | LD_4 | ')
  V1: @mf REPEAT(2, `LD_3 | LD_4 | LD_1 | LD_2 | ')
  V1: @diminuendo LD_2 | LD_1 | r/1 | r/1 |
