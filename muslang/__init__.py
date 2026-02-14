"""
Muslang: A Music Composition DSL with Extensive Articulation Support

This package provides a domain-specific language for composing music with
extensive support for articulations, dynamics, ornaments, and expressive notation.

Main Components:
- Parser: Converts .mus source files to AST
- Semantic Analyzer: Validates and transforms the AST
- MIDI Generator: Produces MIDI files from the AST

Example:
    from muslang import compile_file
    
    compile_file('melody.mus', 'output.mid')
"""

__version__ = "0.1.0"
__author__ = "Muslang Contributors"

# Main API will be added as modules are implemented
__all__ = []
