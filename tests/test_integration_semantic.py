"""
Integration test for semantic analysis with key signatures and ornaments
"""

import pytest
from muslang.parser import parse_muslang
from muslang.semantics import SemanticAnalyzer


def test_key_signature_application():
    """Test key signature application through full pipeline"""
    source = """
    piano: (key g 'major)
      f4/4 c4/4 g4/4
    """
    
    # Parse
    ast = parse_muslang(source)
    
    # Analyze
    analyzer = SemanticAnalyzer()
    result = analyzer.analyze(ast)
    
    # Check that key signature is present
    instrument = result.instruments['piano']
    assert any(hasattr(e, 'root') and e.root == 'g' for e in instrument.events)
    
    # Check that F notes should have sharp accidental applied
    f_notes = [e for e in instrument.events if hasattr(e, 'pitch') and e.pitch == 'f']
    for note in f_notes:
        # F in G major should become F#
        assert note.accidental == 'sharp'


def test_ornament_expansion():
    """Test ornament expansion through full pipeline"""
    source = """
    piano: %trill c4/4
    """
    
    # Parse
    ast = parse_muslang(source)
    
    # Analyze
    analyzer = SemanticAnalyzer()
    result = analyzer.analyze(ast)
    
    # After expansion, trill should generate 8 notes
    instrument = result.instruments['piano']
    notes = [e for e in instrument.events if hasattr(e, 'pitch')]
    
    # Should have 8 notes from the trill expansion
    assert len(notes) == 8


def test_repeat_expansion():
    """Test repeat expansion"""
    source = """
    piano: [c4/4 d4/4 e4/4] * 3
    """
    
    # Parse
    ast = parse_muslang(source)
    
    # Analyze
    analyzer = SemanticAnalyzer()
    result = analyzer.analyze(ast)
    
    # Should have 9 notes (3 notes repeated 3 times)
    instrument = result.instruments['piano']
    notes = [e for e in instrument.events if hasattr(e, 'pitch')]
    assert len(notes) == 9


def test_variable_resolution_integration():
    """Test variable resolution through full pipeline"""
    source = """
    piano: 
      motif = [c4/4 e4/4 g4/4]
      $motif $motif
    """
    
    # Parse
    ast = parse_muslang(source)
    
    # Analyze
    analyzer = SemanticAnalyzer()
    result = analyzer.analyze(ast)
    
    # Should have 6 notes (motif played twice)
    instrument = result.instruments['piano']
    notes = [e for e in instrument.events if hasattr(e, 'pitch')]
    assert len(notes) == 6


def test_complex_combination():
    """Test combination of features"""
    source = """
    piano: (key d 'major)
      :staccato
      @f
      [c4/4 d4/4 e4/4] * 2
      %mordent f4/4
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
    assert len(instrument.events) > 0


def test_validation_error_detected():
    """Test that validation errors are detected"""
    # Slur with only one note - this is invalid
    source = """
    piano: {c4/4}
    """
    
    # Parse
    ast = parse_muslang(source)
    
    # Analyze should raise error for slur with too few notes
    analyzer = SemanticAnalyzer()
    
    from muslang.semantics import SemanticError
    with pytest.raises(SemanticError):
        analyzer.analyze(ast)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
