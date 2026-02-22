"""
Tests for Music Theory Module
"""

import pytest
from muslang.ast_nodes import Note, KeySignature
from muslang.theory import (
    KeySignatureInfo,
    get_upper_neighbor,
    get_lower_neighbor,
    expand_ornament,
    apply_key_signature_to_note
)


def test_key_signature_c_major():
    """Test C major key signature (no accidentals)"""
    key = KeySignatureInfo('c', 'major')
    
    assert len(key.accidentals) == 0
    assert not key.affects_pitch('c')
    assert not key.affects_pitch('d')
    assert not key.affects_pitch('f')


def test_key_signature_g_major():
    """Test G major key signature (F#)"""
    key = KeySignatureInfo('g', 'major')
    
    assert len(key.accidentals) == 1
    assert key.affects_pitch('f')
    assert key.get_accidental('f') == 'sharp'
    assert not key.affects_pitch('c')


def test_key_signature_d_major():
    """Test D major key signature (F#, C#)"""
    key = KeySignatureInfo('d', 'major')
    
    assert len(key.accidentals) == 2
    assert key.affects_pitch('f')
    assert key.affects_pitch('c')
    assert key.get_accidental('f') == 'sharp'
    assert key.get_accidental('c') == 'sharp'


def test_key_signature_f_major():
    """Test F major key signature (Bb)"""
    key = KeySignatureInfo('f', 'major')
    
    assert len(key.accidentals) == 1
    assert key.affects_pitch('b')
    assert key.get_accidental('b') == 'flat'


def test_key_signature_a_minor():
    """Test A minor key signature (no accidentals, natural minor)"""
    key = KeySignatureInfo('a', 'minor')
    
    assert len(key.accidentals) == 0
    assert not key.affects_pitch('c')
    assert not key.affects_pitch('f')


def test_key_signature_e_minor():
    """Test E minor key signature (F#)"""
    key = KeySignatureInfo('e', 'minor')
    
    assert len(key.accidentals) == 1
    assert key.affects_pitch('f')
    assert key.get_accidental('f') == 'sharp'


def test_get_upper_neighbor_no_key():
    """Test getting upper neighbor without key signature"""
    note = Note(pitches=[('c', 4, None)], duration=4)
    upper = get_upper_neighbor(note)
    
    assert upper.pitches[0][0] == 'd'
    assert upper.pitches[0][1] == 4
    assert upper.duration == 32  # Grace note duration


def test_get_upper_neighbor_octave_wrap():
    """Test upper neighbor wraps to next octave at B"""
    note = Note(pitches=[('b', 4, None)], duration=4)
    upper = get_upper_neighbor(note)
    
    assert upper.pitches[0][0] == 'c'
    assert upper.pitches[0][1] == 5  # Should wrap to next octave


def test_get_upper_neighbor_with_key():
    """Test upper neighbor respects key signature"""
    key = KeySignatureInfo('g', 'major')  # F#
    note = Note(pitches=[('e', 4, None)], duration=4)
    upper = get_upper_neighbor(note, key)
    
    assert upper.pitches[0][0] == 'f'
    assert upper.pitches[0][2] == 'sharp'  # Should be F# in G major


def test_get_lower_neighbor_no_key():
    """Test getting lower neighbor without key signature"""
    note = Note(pitches=[('d', 4, None)], duration=4)
    lower = get_lower_neighbor(note)
    
    assert lower.pitches[0][0] == 'c'
    assert lower.pitches[0][1] == 4
    assert lower.duration == 32


def test_get_lower_neighbor_octave_wrap():
    """Test lower neighbor wraps to previous octave at C"""
    note = Note(pitches=[('c', 4, None)], duration=4)
    lower = get_lower_neighbor(note)
    
    assert lower.pitches[0][0] == 'b'
    assert lower.pitches[0][1] == 3  # Should wrap to previous octave


def test_get_lower_neighbor_with_key():
    """Test lower neighbor respects key signature"""
    key = KeySignatureInfo('f', 'major')  # Bb
    note = Note(pitches=[('c', 4, None)], duration=4)
    lower = get_lower_neighbor(note, key)
    
    assert lower.pitches[0][0] == 'b'
    assert lower.pitches[0][2] == 'flat'  # Should be Bb in F major


def test_expand_trill():
    """Test trill expansion"""
    note = Note(pitches=[('c', 4, None)], duration=4)
    notes = expand_ornament('trill', note)
    
    assert len(notes) == 8  # 8 fast notes
    # Should alternate between main note and upper neighbor
    assert notes[0].pitches[0][0] == 'c'
    assert notes[1].pitches[0][0] == 'd'
    assert notes[2].pitches[0][0] == 'c'
    assert notes[3].pitches[0][0] == 'd'


def test_expand_trill_with_key():
    """Test trill expansion with key signature"""
    key = KeySignatureInfo('g', 'major')  # F#
    note = Note(pitches=[('e', 4, None)], duration=4)
    notes = expand_ornament('trill', note, key)
    
    assert len(notes) == 8
    # Should trill to F# (upper neighbor in G major)
    assert notes[1].pitches[0][0] == 'f'
    assert notes[1].pitches[0][2] == 'sharp'


def test_expand_trill_fills_note_duration():
    """Trill expansion should preserve total duration of principal note"""
    note = Note(pitches=[('c', 4, None)], duration=2)  # half note
    notes = expand_ornament('trill', note)

    total_units = 0
    for expanded_note in notes:
        base_units = 128 // expanded_note.duration
        if expanded_note.dotted:
            base_units = (base_units * 3) // 2
        total_units += base_units

    # Half note = 64 1/128-note units
    assert total_units == 64


def test_expand_mordent():
    """Test mordent expansion"""
    note = Note(pitches=[('d', 4, None)], duration=4)
    notes = expand_ornament('mordent', note)
    
    assert len(notes) == 3  # Main, lower, main
    assert notes[0].pitches[0][0] == 'd'
    assert notes[1].pitches[0][0] == 'c'  # Lower neighbor
    assert notes[2].pitches[0][0] == 'd'

    total_units = 0
    for expanded_note in notes:
        base_units = 128 // expanded_note.duration
        if expanded_note.dotted:
            base_units = (base_units * 3) // 2
        total_units += base_units
    assert total_units == 32  # Quarter note duration preserved


def test_expand_turn():
    """Test turn expansion"""
    note = Note(pitches=[('d', 4, None)], duration=4)
    notes = expand_ornament('turn', note)
    
    assert len(notes) == 4  # Upper, main, lower, main
    assert notes[0].pitches[0][0] == 'e'  # Upper neighbor
    assert notes[1].pitches[0][0] == 'd'  # Main
    assert notes[2].pitches[0][0] == 'c'  # Lower neighbor
    assert notes[3].pitches[0][0] == 'd'  # Main

    total_units = 0
    for expanded_note in notes:
        base_units = 128 // expanded_note.duration
        if expanded_note.dotted:
            base_units = (base_units * 3) // 2
        total_units += base_units
    assert total_units == 32  # Quarter note duration preserved


def test_expand_tremolo():
    """Test tremolo expansion"""
    note = Note(pitches=[('d', 4, None)], duration=4)
    notes = expand_ornament('tremolo', note)

    assert len(notes) == 4  # 4 x 16th notes in a quarter note
    assert all(n.pitches[0][0] == 'd' for n in notes)
    assert all(n.duration == 16 for n in notes)


def test_apply_key_signature_to_note():
    """Test applying key signature to note"""
    key = KeySignatureInfo('g', 'major')  # F#
    note = Note(pitches=[('f', 4, None)], duration=4)
    
    result = apply_key_signature_to_note(note, key)
    
    assert result.pitches[0][0] == 'f'
    assert result.pitches[0][2] == 'sharp'


def test_apply_key_signature_preserves_explicit_accidental():
    """Test that explicit accidentals are not overridden"""
    key = KeySignatureInfo('g', 'major')  # F#
    note = Note(pitches=[('f', 4, 'natural')], duration=4)
    
    result = apply_key_signature_to_note(note, key)
    
    # Should preserve the natural accidental
    assert result.pitches[0][2] == 'natural'


def test_apply_key_signature_unaffected_pitch():
    """Test that unaffected pitches remain unchanged"""
    key = KeySignatureInfo('g', 'major')  # F#
    note = Note(pitches=[('c', 4, None)], duration=4)
    
    result = apply_key_signature_to_note(note, key)
    
    assert result.pitches[0][0] == 'c'
    assert result.pitches[0][2] is None  # Should remain None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
