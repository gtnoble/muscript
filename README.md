# Muslang

A music composition DSL (Domain-Specific Language) with extensive articulation support that compiles to MIDI files.

## Overview

Muslang is a Python-based music composition language that allows composers to write music using an intuitive text-based syntax inspired by Alda. The language provides extensive support for:

- **Articulations**: legato, staccato, tenuto, marcato
- **Dynamics**: pp, p, mp, mf, f, ff with crescendo/diminuendo
- **Ornaments**: trills, mordents, turns, tremolo
- **Rhythm**: tuplets, grace notes, ties, dotted notes
- **Phrase groupings**: slurs, slides (chromatic, stepped, portamento)
- **Musical structure**: multiple instruments, voices, key signatures, time signatures
- **Macro workflow**: external `m4` preprocessing for reusable motifs/patterns
- **Percussion**: comprehensive drum notation

## Installation

```bash
pip install muslang
```

Or install from source:

```bash
git clone https://github.com/yourusername/muslang.git
cd muslang
pip install -e .
```

## Quick Start

Create a file `melody.mus`:

```muslang
# Simple melody - using scientific pitch notation
# Format: pitch+octave/duration (e.g., c4/4 = C octave 4, quarter note)
# All notes must be in a voice (V1:, V2:, etc.)
piano (tempo! 120) (time 4 4) {
  V1: c4/4 d4/4 e4/4 f4/4 | g4/2 g4/2 | a4/4 a4/4 a4/4 a4/4 | g4/1
}
```

Compile to MIDI:

```bash
# Using python module
python -m muslang.cli compile melody.mus -o melody.mid

# Or if installed as package
muslang compile melody.mus -o melody.mid
```

### Optional macro preprocessing with `m4`

Muslang base syntax no longer includes built-in variables or repeat blocks. For reusable patterns, preprocess a `.mus.m4` source file with `m4`, then compile the generated `.mus` file.

You can implement repeats with recursive `m4` macros, for example:

```m4
define(`REPEAT', `ifelse($1, `0', `', `$2`'REPEAT(decr($1), `$2')')')
define(`RIFF', `c4/8 e4/8 g4/8 e4/8')
# Usage inside a voice: REPEAT(4, `RIFF ')
```

```bash
m4 examples/repeat_demo.mus.m4 > examples/repeat_demo.mus
python -m muslang.cli compile examples/repeat_demo.mus -o examples/repeat_demo.mid
```

Check syntax:

```bash
python -m muslang.cli check melody.mus
```

Play the MIDI file:

```bash
python -m muslang.cli play melody.mus
```

## CLI Commands

### compile
Compile a .mus file to MIDI:
```bash
python -m muslang.cli compile input.mus [-o output.mid] [--ppq 480] [-v]
```
- `-o, --output`: Output MIDI file path (default: input.mid)
- `--ppq`: MIDI resolution in pulses per quarter note (default: 480)
- `-v, --verbose`: Print detailed compilation information

### check
Validate syntax and semantics:
```bash
python -m muslang.cli check input.mus [-v]
```
- `-v, --verbose`: Print detailed validation information

### play
Compile and play immediately:
```bash
python -m muslang.cli play input.mus [--player fluidsynth] [--soundfont path/to/soundfont.sf2]
```
- `--player`: Choose MIDI player (fluidsynth or timidity)
- `--soundfont`: Path to soundfont file (for fluidsynth)

## Language Features

### Basic Notes - Scientific Pitch Notation

Muslang uses scientific pitch notation where each note specifies both pitch and octave:
- Format: `pitch` + `octave` + `/` + `duration`
- Example: `c4/4` = C octave 4, quarter note
- Middle C is `c4`

```muslang
piano {
  V1: c4/4 d4/4 e4/4 f4/4  # Quarter notes C4, D4, E4, F4
      c4/2 d4/2             # Half notes
      c4/1                  # Whole note
      c4/8 d4/8 e4/8 f4/8  # Eighth notes
}
```

### Accidentals

```muslang
piano {
  V1: c4+/4 d4-/4 e4/4  # C sharp, D flat, E natural (quarter notes)
}
```

### Articulations (: prefix)

```muslang
piano {
  V1: :staccato c4/4 d4/4 e4/4 f4/4  # Staccato notes
      :legato g4/4 a4/4 b4/4 c5/4     # Legato notes
      :reset d4/4 e4/4 f4/4 g4/4      # Back to natural
      :tenuto c4/4 e4/4 g4/4          # Tenuto
      :marcato c4/4 e4/4 g4/4         # Marcato (accented)
}
```

### Dynamics (@ prefix)

```muslang
piano {
  V1: @p c4/4 d4/4 e4/4 f4/4           # Piano (soft)
      @f g4/4 a4/4 b4/4 c5/4           # Forte (loud)
      @crescendo c4/4 d4/4 e4/4 f4/4   # Gradual increase
      @diminuendo c5/4 b4/4 a4/4 g4/4  # Gradual decrease
      @sforzando c4/4                  # Sudden accent
}
```

### Legato and Slides

```muslang
piano {
  V1: :legato c4/4 d4/4 e4/4 f4/4   # Slurred phrase via articulation
      <c4/4 g4/4>                   # Chromatic slide
      <portamento: c4/4 g4/4>       # Portamento slide
      <stepped: c4/4 g4/4>          # Stepped slide
}
```

### Ornaments (% prefix)

```muslang
piano {
  V1: %trill c4/4    # Trill on C
      %mordent d4/4  # Mordent on D
      %turn e4/4     # Turn on E
      %tremolo g4/2  # Tremolo
}
```

### Tuplets

```muslang
piano {
  V1: (c4/8 d4/8 e4/8):3   # Triplet of eighth notes
      (c4/16 d4/16 e4/16 f4/16 g4/16):5  # Quintuplet
}
```

### Chords (comma-separated)

```muslang
piano {
  V1: c4/4,e4/4,g4/4   # C major chord (quarter notes)
      c4/2,e4-/2,g4/2  # C minor chord (half notes)
}
```

### Multiple Instruments

```muslang
piano {
  V1: c4/4 e4/4 g4/4 c5/4
}
violin {
  V1: e4/4 g4/4 b4/4 e5/4
}
bass {
  V1: c2/2 c2/2
}
```

## Development

### Running Tests

```bash
pip install -e ".[dev]"
pytest
```

### Running with Coverage

```bash
pytest --cov=muslang --cov-report=html
```

## Project Structure

```
muslang/
├── muslang/           # Main package
│   ├── ast_nodes.py   # AST node definitions
│   ├── grammar.lark   # Lark grammar
│   ├── parser.py      # Parser & transformer
│   ├── semantics.py   # Semantic analysis
│   ├── articulations.py  # Articulation mapping
│   ├── midi_gen.py    # MIDI generation
│   ├── cli.py         # Command-line interface
│   └── config.py      # Configuration & constants
├── tests/             # Test suite
├── examples/          # Example compositions
└── docs/              # Documentation
```

## Documentation

- [Syntax Reference](docs/syntax_reference.md)
- [Articulation Guide](docs/articulation_guide.md)
- [Rhythm Guide](docs/rhythm_guide.md)
- [Ornaments Guide](docs/ornaments_guide.md)
- [Percussion Guide](docs/percussion_guide.md)

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

Inspired by [Alda](https://alda.io/), the music programming language.
