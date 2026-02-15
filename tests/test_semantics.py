"""
Tests for Semantic Analysis Phase
"""

import pytest
from muslang.ast_nodes import *
from muslang.semantics import SemanticAnalyzer, SemanticError


def test_semantic_analyzer_creation():
    """Test creating a semantic analyzer"""
    analyzer = SemanticAnalyzer()
    assert analyzer is not None
    assert len(analyzer.errors) == 0
    assert len(analyzer.warnings) == 0


def test_validate_note_octave_range():
    """Test note octave validation"""
    analyzer = SemanticAnalyzer()
    
    # Invalid octave - too low
    note = Note(pitch='c', octave=-1, duration=4)
    instrument = Instrument(name='piano', events=[], voices={1: [note]})
    ast = Sequence(events=[instrument])
    
    analyzer._validate_ast(ast)
    assert len(analyzer.errors) > 0
    assert "Octave out of range" in analyzer.errors[0]


def test_validate_note_octave_range_too_high():
    """Test note octave validation - too high"""
    analyzer = SemanticAnalyzer()
    
    # Invalid octave - too high
    note = Note(pitch='c', octave=11, duration=4)
    instrument = Instrument(name='piano', events=[], voices={1: [note]})
    ast = Sequence(events=[instrument])
    
    analyzer._validate_ast(ast)
    assert len(analyzer.errors) > 0
    assert "Octave out of range" in analyzer.errors[0]


def test_validate_valid_octave():
    """Test that valid octaves don't generate errors"""
    analyzer = SemanticAnalyzer()
    
    # Valid octaves
    for octave in [0, 4, 8, 10]:
        note = Note(pitch='c', octave=octave, duration=4)
        instrument = Instrument(name='piano', events=[], voices={1: [note]})
        ast = Sequence(events=[instrument])
        
        analyzer.errors = []
        analyzer._validate_ast(ast)
        assert len(analyzer.errors) == 0


def test_validate_note_duration():
    """Test note duration validation"""
    analyzer = SemanticAnalyzer()
    
    # Invalid duration
    note = Note(pitch='c', octave=4, duration=3)  # 3 is not valid
    instrument = Instrument(name='piano', events=[], voices={1: [note]})
    ast = Sequence(events=[instrument])
    
    analyzer._validate_ast(ast)
    assert len(analyzer.errors) > 0
    assert "Invalid duration" in analyzer.errors[0]


def test_validate_valid_durations():
    """Test that valid durations don't generate errors"""
    analyzer = SemanticAnalyzer()
    
    valid_durations = [1, 2, 4, 8, 16, 32, 64]
    for duration in valid_durations:
        note = Note(pitch='c', octave=4, duration=duration)
        instrument = Instrument(name='piano', events=[], voices={1: [note]})
        ast = Sequence(events=[instrument])
        
        analyzer.errors = []
        analyzer._validate_ast(ast)
        assert len(analyzer.errors) == 0


def test_validate_slur_minimum_notes():
    """Test slur with too few notes"""
    analyzer = SemanticAnalyzer()
    
    # Slur with only one note
    note = Note(pitch='c', octave=4, duration=4)
    slur = Slur(notes=[note])
    instrument = Instrument(name='piano', events=[], voices={1: [slur]})
    ast = Sequence(events=[instrument])
    
    analyzer._validate_ast(ast)
    assert len(analyzer.errors) > 0
    assert "at least 2 notes" in analyzer.errors[0]


def test_validate_tuplet_ratio():
    """Test tuplet ratio validation"""
    analyzer = SemanticAnalyzer()
    
    # Invalid tuplet ratio
    note = Note(pitch='c', octave=4, duration=8)
    tuplet = Tuplet(notes=[note], ratio=1, actual_duration=2)
    instrument = Instrument(name='piano', events=[], voices={1: [tuplet]})
    ast = Sequence(events=[instrument])
    
    analyzer._validate_ast(ast)
    assert len(analyzer.errors) > 0
    assert "Tuplet ratio must be >= 2" in analyzer.errors[0]


def test_validate_time_signature():
    """Test time signature validation"""
    analyzer = SemanticAnalyzer()
    
    # Invalid numerator
    time_sig = TimeSignature(numerator=0, denominator=4)
    instrument = Instrument(name='piano', events=[time_sig], voices={1: []})
    ast = Sequence(events=[instrument])
    
    analyzer._validate_ast(ast)
    assert len(analyzer.errors) > 0
    assert "numerator must be >= 1" in analyzer.errors[0]


def test_validate_time_signature_denominator():
    """Test time signature denominator validation"""
    analyzer = SemanticAnalyzer()
    
    # Invalid denominator
    time_sig = TimeSignature(numerator=4, denominator=3)
    instrument = Instrument(name='piano', events=[time_sig], voices={1: []})
    ast = Sequence(events=[instrument])
    
    analyzer._validate_ast(ast)
    assert len(analyzer.errors) > 0
    assert "Invalid time signature denominator" in analyzer.errors[0]


def test_validate_tempo_warning():
    """Test tempo validation generates warning for unusual values"""
    analyzer = SemanticAnalyzer()
    
    # Very slow tempo
    tempo = Tempo(bpm=10)
    instrument = Instrument(name='piano', events=[tempo], voices={1: []})
    ast = Sequence(events=[instrument])
    
    analyzer._validate_ast(ast)
    assert len(analyzer.warnings) > 0
    assert "Unusual tempo" in analyzer.warnings[0]


def test_validate_slide_large_interval_warning():
    """Test slide with large interval generates warning"""
    analyzer = SemanticAnalyzer()
    
    # Large interval slide (more than 2 octaves)
    from_note = Note(pitch='c', octave=2, duration=4)
    to_note = Note(pitch='c', octave=5, duration=4)
    slide = Slide(from_note=from_note, to_note=to_note)
    instrument = Instrument(name='piano', events=[], voices={1: [slide]})
    ast = Sequence(events=[instrument])
    
    analyzer._validate_ast(ast)
    assert len(analyzer.warnings) > 0
    assert "Large slide interval" in analyzer.warnings[0]


def test_note_to_midi():
    """Test note to MIDI conversion"""
    analyzer = SemanticAnalyzer()
    
    # Middle C (C4) should be MIDI note 60
    note = Note(pitch='c', octave=4, duration=4)
    midi = analyzer._note_to_midi(note)
    assert midi == 60
    
    # A4 should be MIDI note 69
    note = Note(pitch='a', octave=4, duration=4)
    midi = analyzer._note_to_midi(note)
    assert midi == 69
    
    # C5 (high C) should be MIDI note 72
    note = Note(pitch='c', octave=5, duration=4)
    midi = analyzer._note_to_midi(note)
    assert midi == 72


def test_note_to_midi_with_accidentals():
    """Test note to MIDI conversion with accidentals"""
    analyzer = SemanticAnalyzer()
    
    # C#4 should be MIDI note 61
    note = Note(pitch='c', octave=4, duration=4, accidental='sharp')
    midi = analyzer._note_to_midi(note)
    assert midi == 61
    
    # Db4 should be MIDI note 61 (same as C#4)
    note = Note(pitch='d', octave=4, duration=4, accidental='flat')
    midi = analyzer._note_to_midi(note)
    assert midi == 61
    
    # Bb3 should be MIDI note 58
    note = Note(pitch='b', octave=3, duration=4, accidental='flat')
    midi = analyzer._note_to_midi(note)
    assert midi == 58


def test_full_analysis_pipeline():
    """Test full analysis pipeline with simple AST"""
    analyzer = SemanticAnalyzer()
    
    # Create simple AST
    note1 = Note(pitch='c', octave=4, duration=4)
    note2 = Note(pitch='e', octave=4, duration=4)
    note3 = Note(pitch='g', octave=4, duration=4)
    instrument = Instrument(name='piano', events=[], voices={1: [note1, note2, note3]})
    ast = Sequence(events=[instrument])
    
    # Should not raise any errors
    result = analyzer.analyze(ast)
    
    assert result is not None
    assert isinstance(result, Sequence)
    assert len(analyzer.errors) == 0


def test_analysis_with_errors_raises():
    """Test that analysis with errors raises SemanticError"""
    analyzer = SemanticAnalyzer()
    
    # Create AST with error (invalid octave)
    note = Note(pitch='c', octave=11, duration=4)
    instrument = Instrument(name='piano', events=[], voices={1: [note]})
    ast = Sequence(events=[instrument])
    
    with pytest.raises(SemanticError):
        analyzer.analyze(ast)


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])
