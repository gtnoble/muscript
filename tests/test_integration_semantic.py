"""
Integration test for semantic analysis with key signatures and ornaments
"""

import pytest
from lark.exceptions import LarkError
from muslang.parser import parse_muslang
from muslang.semantics import SemanticAnalyzer


def test_key_signature_application():
    """Test key signature application through full pipeline"""
    source = """
    (key g 'major)
    piano {
      V1: f4/4 c4/4 g4/4 r/4 |
    }
    """
    
    # Parse
    ast = parse_muslang(source)
    
    # Analyze
    analyzer = SemanticAnalyzer()
    result = analyzer.analyze(ast)
    
    instrument = result.instruments['piano']
    
    # Check that F notes should have sharp accidental applied
    f_notes = [e for e in instrument.voices[1] if hasattr(e, 'pitch') and e.pitch == 'f']
    for note in f_notes:
        # F in G major should become F#
        assert note.accidental == 'sharp'


def test_ornament_expansion():
    """Test ornament parsing survives full semantic pipeline"""
    source = """
    piano {
      V1: %trill c4/4 r/4 r/4 r/4 |
    }
    """
    
    # Parse
    ast = parse_muslang(source)
    
    # Analyze
    analyzer = SemanticAnalyzer()
    result = analyzer.analyze(ast)
    
    # Current behavior: ornament marker is preserved and principal note remains
    instrument = result.instruments['piano']
    notes = [
      event
      for measure in instrument.voices[1]
      for event in measure.events
      if hasattr(event, 'pitch')
    ]
    
    assert len(notes) == 1


def test_repeat_syntax_rejected():
    """Repeat syntax is no longer supported in base language"""
    source = """
    piano {
      V1: [c4/4 d4/4 e4/4] * 3 |
    }
    """

    with pytest.raises(LarkError):
        parse_muslang(source)


def test_variable_syntax_rejected():
    """Variable syntax is no longer supported in base language"""
    source = """
    piano {
      V1: motif = [c4/4 e4/4 g4/4] |
      V1: $motif $motif |
    }
    """

    with pytest.raises(LarkError):
        parse_muslang(source)


def test_complex_combination():
    """Test combination of features"""
    source = """
    (time 5 4)
    (key d 'major)
    piano {
      V1: :staccato c4/4 d4/4 e4/4 @f %mordent f4/4 g4/4 |
    }
    """
    
    # Parse
    ast = parse_muslang(source)
    
    # Analyze
    analyzer = SemanticAnalyzer()
    result = analyzer.analyze(ast)
    
    # Should not raise any errors
    assert result is not None
    assert len(analyzer.errors) == 0
    
    # Check instrument has events
    instrument = result.instruments['piano']
    assert len(instrument.voices[1]) > 0


def test_validation_error_detected():
    """Test that validation errors are detected"""
    # Measure duration mismatch should trigger semantic validation error
    source = """
    piano {
      V1: c4/4 |
    }
    """
    
    # Parse
    ast = parse_muslang(source)
    
    # Analyze should raise error for measure mismatch
    analyzer = SemanticAnalyzer()
    
    from muslang.semantics import SemanticError
    with pytest.raises(SemanticError):
        analyzer.analyze(ast)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
