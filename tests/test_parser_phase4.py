"""
Quick test for Phase 4 parser implementation.
"""
from muslang.parser import parse_muslang
from muslang.ast_nodes import Instrument, Note, Chord, Articulation, DynamicLevel

def test_basic_notes():
    """Test parsing basic notes with scientific pitch notation."""
    source = """
    piano:
      V1: c4/4 d4/4 e4/4 f4/4
    """
    ast = parse_muslang(source)
    
    assert len(ast.instruments) == 1
    instrument = ast.instruments['piano']
    assert isinstance(instrument, Instrument)
    assert instrument.name == "piano"
    assert len(instrument.voices[1]) == 4
    
    # Check first note: c4/4
    note1 = instrument.voices[1][0]
    assert isinstance(note1, Note)
    assert note1.pitch == 'c'
    assert note1.octave == 4
    assert note1.duration == 4
    assert note1.dotted == False
    assert note1.accidental is None
    
    print("✓ Basic notes test passed")

def test_articulations():
    """Test articulation parsing with colon prefix."""
    source = """
    piano:
      V1: :staccato c4/4 d4/4 :legato e4/4 f4/4
    """
    ast = parse_muslang(source)
    
    instrument = ast.instruments['piano']
    voice_events = instrument.voices[1]
    assert len(voice_events) == 6  # 2 articulations + 4 notes
    
    # First event should be staccato articulation
    assert isinstance(voice_events[0], Articulation)
    assert voice_events[0].type == 'staccato'
    
    # Fourth event should be legato articulation (not third!)
    assert isinstance(voice_events[3], Articulation)
    assert voice_events[3].type == 'legato'
    
    print("✓ Articulations test passed")

def test_dynamics():
    """Test dynamic markings with @ prefix."""
    source = """
    piano:
      V1: @p c4/4 @f d4/4
    """
    ast = parse_muslang(source)
    
    instrument = ast.instruments['piano']
    voice_events = instrument.voices[1]
    assert len(voice_events) == 4  # 2 dynamics + 2 notes
    
    # First event should be piano dynamic
    assert isinstance(voice_events[0], DynamicLevel)
    assert voice_events[0].level == 'p'
    
    # Third event should be forte dynamic
    assert isinstance(voice_events[2], DynamicLevel)
    assert voice_events[2].level == 'f'
    
    print("✓ Dynamics test passed")

def test_chord():
    """Test chord parsing with comma separator."""
    source = """
    piano:
      V1: c4/4,e4/4,g4/4
    """
    ast = parse_muslang(source)
    
    instrument = ast.instruments['piano']
    voice_events = instrument.voices[1]
    assert len(voice_events) == 1
    
    # Should be a chord
    chord = voice_events[0]
    assert isinstance(chord, Chord)
    assert len(chord.notes) == 3
    assert chord.notes[0].pitch == 'c'
    assert chord.notes[1].pitch == 'e'
    assert chord.notes[2].pitch == 'g'
    
    print("✓ Chord test passed")

def test_accidentals():
    """Test sharp and flat accidentals."""
    source = """
    piano:
      V1: c4+/4 d4-/4 e4/4
    """
    ast = parse_muslang(source)
    
    instrument = ast.instruments['piano']
    voice_events = instrument.voices[1]
    assert len(voice_events) == 3
    
    # C sharp
    assert voice_events[0].accidental == 'sharp'
    
    # D flat
    assert voice_events[1].accidental == 'flat'
    
    # E natural (no accidental)
    assert voice_events[2].accidental is None
    
    print("✓ Accidentals test passed")

def test_dotted_and_tied():
    """Test dotted notes and ties."""
    source = """
    piano:
      V1: c4/4. d4/4~ e4/4
    """
    ast = parse_muslang(source)
    
    instrument = ast.instruments['piano']
    voice_events = instrument.voices[1]
    
    # C dotted quarter
    assert voice_events[0].dotted == True
    assert voice_events[0].tied == False
    
    # D quarter tied
    assert voice_events[1].dotted == False
    assert voice_events[1].tied == True
    
    # E quarter (normal)
    assert voice_events[2].dotted == False
    assert voice_events[2].tied == False
    
    print("✓ Dotted and tied notes test passed")

def test_rest_duration_parsing():
    """Test explicit rest durations are parsed correctly."""
    from muslang.ast_nodes import Rest

    source = """
    piano:
      V1: r/16 c4/4 r/8
    """
    ast = parse_muslang(source)

    voice_events = ast.instruments['piano'].voices[1]
    assert isinstance(voice_events[0], Rest)
    assert voice_events[0].duration == 16
    assert voice_events[0].dotted is False

    assert isinstance(voice_events[2], Rest)
    assert voice_events[2].duration == 8
    assert voice_events[2].dotted is False

    print("✓ Rest duration parsing test passed")

def test_dotted_rest_parsing():
    """Test dotted rests are parsed correctly."""
    from muslang.ast_nodes import Rest

    source = """
    piano:
      V1: c4/8 r/8. d4/8
    """
    ast = parse_muslang(source)

    voice_events = ast.instruments['piano'].voices[1]
    assert isinstance(voice_events[1], Rest)
    assert voice_events[1].duration == 8
    assert voice_events[1].dotted is True

    print("✓ Dotted rest parsing test passed")

def test_directives():
    """Test tempo, time signature, and key signature."""
    from muslang.ast_nodes import Tempo, TimeSignature, KeySignature
    
    source = """
    piano: (tempo! 120) (time 4 4) (key c 'major)
      V1: c4/4
    """
    ast = parse_muslang(source)
    
    instrument = ast.instruments['piano']
    
    # Check tempo (directives are at instrument level)
    assert isinstance(instrument.events[0], Tempo)
    assert instrument.events[0].bpm == 120
    
    # Check time signature
    assert isinstance(instrument.events[1], TimeSignature)
    assert instrument.events[1].numerator == 4
    assert instrument.events[1].denominator == 4
    
    # Check key signature
    assert isinstance(instrument.events[2], KeySignature)
    assert instrument.events[2].root == 'c'
    assert instrument.events[2].mode == 'major'
    
    print("✓ Directives test passed")

def test_slur():
    """Test slur grouping."""
    from muslang.ast_nodes import Slur
    
    source = """
    piano:
      V1: {c4/4 d4/4 e4/4}
    """
    ast = parse_muslang(source)
    
    instrument = ast.instruments['piano']
    voice_events = instrument.voices[1]
    assert len(voice_events) == 1
    
    slur = voice_events[0]
    assert isinstance(slur, Slur)
    assert len(slur.notes) == 3
    
    print("✓ Slur test passed")

def test_slide():
    """Test slide/glissando."""
    from muslang.ast_nodes import Slide
    
    source = """
    piano:
      V1: <c4/4 c5/4>
    """
    ast = parse_muslang(source)
    
    instrument = ast.instruments['piano']
    voice_events = instrument.voices[1]
    assert len(voice_events) == 1
    
    slide = voice_events[0]
    assert isinstance(slide, Slide)
    assert slide.from_note.pitch == 'c'
    assert slide.from_note.octave == 4
    assert slide.to_note.pitch == 'c'
    assert slide.to_note.octave == 5
    assert slide.style == 'chromatic'
    
    print("✓ Slide test passed")

def test_multiple_instruments():
    """Test multiple instruments."""
    source = """
    piano:
      V1: c4/4 d4/4
    guitar:
      V1: e4/4 f4/4
    """
    ast = parse_muslang(source)
    
    assert len(ast.instruments) == 2
    assert 'piano' in ast.instruments
    assert 'guitar' in ast.instruments
    assert ast.instruments['piano'].name == "piano"
    assert ast.instruments['guitar'].name == "guitar"
    
    print("✓ Multiple instruments test passed")

if __name__ == "__main__":
    print("Testing Phase 4 Parser Implementation\n")
    
    try:
        test_basic_notes()
        test_articulations()
        test_dynamics()
        test_chord()
        test_accidentals()
        test_dotted_and_tied()
        test_rest_duration_parsing()
        test_dotted_rest_parsing()
        test_directives()
        test_slur()
        test_slide()
        test_multiple_instruments()
        
        print("\n✅ All Phase 4 parser tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
