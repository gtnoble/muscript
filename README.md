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
- **Programming constructs**: variables, repeats
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
# Simple melody
piano: (tempo! 120) (time 4 4) o4
  c4 d4 e4 f4 | g2 g2 | a4 a4 a4 a4 | g1
```

Compile to MIDI:

```bash
muslang compile melody.mus -o melody.mid
```

Play the MIDI file:

```bash
muslang play melody.mus
```

## Language Features

### Basic Notes

```muslang
piano: c4 d4 e4 f4  # Quarter notes C, D, E, F
```

### Accidentals

```muslang
piano: c+4 d-4 e4  # C sharp, D flat, E natural
```

### Articulations

```muslang
piano: .staccato c4 d4 e4 f4  # Staccato notes
       .legato g4 a4 b4 c4     # Legato notes
       . d4 e4 f4 g4           # Back to natural
```

### Dynamics

```muslang
piano: .p c4 d4 e4 f4           # Piano (soft)
       .f g4 a4 b4 c4           # Forte (loud)
       .crescendo c4 d4 e4 f4   # Gradual increase
```

### Slurs and Slides

```muslang
piano: {c4 d4 e4 f4}        # Slurred phrase
       <c4 g4>              # Chromatic slide
       <.portamento c4 g4>  # Portamento slide
```

### Ornaments

```muslang
piano: .trill c4    # Trill on C
       .mordent d4  # Mordent on D
       .turn e4     # Turn on E
```

### Tuplets

```muslang
piano: [c8 d e]:3   # Triplet of eighth notes
```

### Multiple Instruments

```muslang
piano: c4 e4 g4 c4
violin: e4 g4 b4 e4
bass: c2 c2
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
