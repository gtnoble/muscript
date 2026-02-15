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
    note = Note(pitch='c', octave=4, duration=4)
    upper = get_upper_neighbor(note)
    
    assert upper.pitch == 'd'
    assert upper.octave == 4
    assert upper.duration == 32  # Grace note duration


def test_get_upper_neighbor_octave_wrap():
    """Test upper neighbor wraps to next octave at B"""
    note = Note(pitch='b', octave=4, duration=4)
    upper = get_upper_neighbor(note)
    
    assert upper.pitch == 'c'
    assert upper.octave == 5  # Should wrap to next octave


def test_get_upper_neighbor_with_key():
    """Test upper neighbor respects key signature"""
    key = KeySignatureInfo('g', 'major')  # F#
    note = Note(pitch='e', octave=4, duration=4)
    upper = get_upper_neighbor(note, key)
    
    assert upper.pitch == 'f'
    assert upper.accidental == 'sharp'  # Should be F# in G major


def test_get_lower_neighbor_no_key():
    """Test getting lower neighbor without key signature"""
    note = Note(pitch='d', octave=4, duration=4)
    lower = get_lower_neighbor(note)
    
    assert lower.pitch == 'c'
    assert lower.octave == 4
    assert lower.duration == 32


def test_get_lower_neighbor_octave_wrap():
    """Test lower neighbor wraps to previous octave at C"""
    note = Note(pitch='c', octave=4, duration=4)
    lower = get_lower_neighbor(note)
    
    assert lower.pitch == 'b'
    assert lower.octave == 3  # Should wrap to previous octave


def test_get_lower_neighbor_with_key():
    """Test lower neighbor respects key signature"""
    key = KeySignatureInfo('f', 'major')  # Bb
    note = Note(pitch='c', octave=4, duration=4)
    lower = get_lower_neighbor(note, key)
    
    assert lower.pitch == 'b'
    assert lower.accidental == 'flat'  # Should be Bb in F major


def test_expand_trill():
    """Test trill expansion"""
    note = Note(pitch='c', octave=4, duration=4)
    notes = expand_ornament('trill', note)
    
    assert len(notes) == 8  # 8 fast notes
    # Should alternate between main note and upper neighbor
    assert notes[0].pitch == 'c'
    assert notes[1].pitch == 'd'
    assert notes[2].pitch == 'c'
    assert notes[3].pitch == 'd'


def test_expand_trill_with_key():
    """Test trill expansion with key signature"""
    key = KeySignatureInfo('g', 'major')  # F#
    note = Note(pitch='e', octave=4, duration=4)
    notes = expand_ornament('trill', note, key)
    
    assert len(notes) == 8
    # Should trill to F# (upper neighbor in G major)
    assert notes[1].pitch == 'f'
    assert notes[1].accidental == 'sharp'


def test_expand_mordent():
    """Test mordent expansion"""
    note = Note(pitch='d', octave=4, duration=4)
    notes = expand_ornament('mordent', note)
    
    assert len(notes) == 3  # Main, lower, main
    assert notes[0].pitch == 'd'
    assert notes[1].pitch == 'c'  # Lower neighbor
    assert notes[2].pitch == 'd'
    assert notes[2].duration == 4  # Last note keeps original duration


def test_expand_turn():
    """Test turn expansion"""
    note = Note(pitch='d', octave=4, duration=4)
    notes = expand_ornament('turn', note)
    
    assert len(notes) == 4  # Upper, main, lower, main
    assert notes[0].pitch == 'e'  # Upper neighbor
    assert notes[1].pitch == 'd'  # Main
    assert notes[2].pitch == 'c'  # Lower neighbor
    assert notes[3].pitch == 'd'  # Main
    assert notes[3].duration == 4  # Last note keeps original duration


def test_apply_key_signature_to_note():
    """Test applying key signature to note"""
    key = KeySignatureInfo('g', 'major')  # F#
    note = Note(pitch='f', octave=4, duration=4)
    
    result = apply_key_signature_to_note(note, key)
    
    assert result.pitch == 'f'
    assert result.accidental == 'sharp'


def test_apply_key_signature_preserves_explicit_accidental():
    """Test that explicit accidentals are not overridden"""
    key = KeySignatureInfo('g', 'major')  # F#
    note = Note(pitch='f', octave=4, duration=4, accidental='natural')
    
    result = apply_key_signature_to_note(note, key)
    
    # Should preserve the natural accidental
    assert result.accidental == 'natural'


def test_apply_key_signature_unaffected_pitch():
    """Test that unaffected pitches remain unchanged"""
    key = KeySignatureInfo('g', 'major')  # F#
    note = Note(pitch='c', octave=4, duration=4)
    
    result = apply_key_signature_to_note(note, key)
    
    assert result.pitch == 'c'
    assert result.accidental is None  # Should remain None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
