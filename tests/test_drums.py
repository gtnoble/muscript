"""
Unit tests for percussion/drum mapping module.
"""

import pytest
from muslang.drums import (
    DRUM_MAP,
    get_drum_midi_note,
    is_percussion_instrument,
    get_all_drum_names,
    validate_drum_name,
)


class TestDrumMap:
    """Tests for DRUM_MAP constant."""
    
    def test_drum_map_exists(self):
        """DRUM_MAP should be defined and non-empty."""
        assert DRUM_MAP is not None
        assert len(DRUM_MAP) > 0
    
    def test_drum_map_has_basic_drums(self):
        """DRUM_MAP should contain basic drum kit pieces."""
        required_drums = ['kick', 'snare', 'hat', 'crash', 'ride']
        for drum in required_drums:
            assert drum in DRUM_MAP, f"Missing basic drum: {drum}"
    
    def test_drum_map_values_are_valid_midi(self):
        """All DRUM_MAP values should be valid MIDI note numbers (0-127)."""
        for drum_name, midi_note in DRUM_MAP.items():
            assert 0 <= midi_note <= 127, (
                f"Invalid MIDI note {midi_note} for drum '{drum_name}'"
            )
    
    def test_drum_map_has_gm_standard_drums(self):
        """DRUM_MAP should include General MIDI standard drums."""
        # General MIDI standard percussion
        assert DRUM_MAP['kick'] == 36  # Bass Drum 1
        assert DRUM_MAP['snare'] == 38  # Acoustic Snare
        assert DRUM_MAP['hat'] == 42  # Closed Hi-Hat
        assert DRUM_MAP['openhat'] == 46  # Open Hi-Hat
        assert DRUM_MAP['crash'] == 49  # Crash Cymbal 1
        assert DRUM_MAP['ride'] == 51  # Ride Cymbal 1


class TestGetDrumMidiNote:
    """Tests for get_drum_midi_note function."""
    
    def test_get_basic_drums(self):
        """Should return correct MIDI notes for basic drums."""
        assert get_drum_midi_note('kick') == 36
        assert get_drum_midi_note('snare') == 38
        assert get_drum_midi_note('hat') == 42
        assert get_drum_midi_note('crash') == 49
        assert get_drum_midi_note('ride') == 51
    
    def test_get_toms(self):
        """Should return correct MIDI notes for toms."""
        assert get_drum_midi_note('tom1') == 48
        assert get_drum_midi_note('tom2') == 47
        assert get_drum_midi_note('tom3') == 45
        assert get_drum_midi_note('tom4') == 43
    
    def test_get_cymbals(self):
        """Should return correct MIDI notes for cymbals."""
        assert get_drum_midi_note('crash') == 49
        assert get_drum_midi_note('crash2') == 57
        assert get_drum_midi_note('splash') == 55
        assert get_drum_midi_note('china') == 52
    
    def test_get_percussion(self):
        """Should return correct MIDI notes for auxiliary percussion."""
        assert get_drum_midi_note('cowbell') == 56
        assert get_drum_midi_note('tambourine') == 54
        assert get_drum_midi_note('clap') == 39
    
    def test_case_insensitive(self):
        """Should work with any case."""
        assert get_drum_midi_note('KICK') == 36
        assert get_drum_midi_note('Snare') == 38
        assert get_drum_midi_note('HaT') == 42
    
    def test_unknown_drum_raises_error(self):
        """Should raise ValueError for unknown drum names."""
        with pytest.raises(ValueError) as exc_info:
            get_drum_midi_note('unknown_drum')
        
        assert 'Unknown drum name' in str(exc_info.value)
        assert 'unknown_drum' in str(exc_info.value)
    
    def test_error_message_includes_available_drums(self):
        """Error message should list available drum names."""
        with pytest.raises(ValueError) as exc_info:
            get_drum_midi_note('invalid')
        
        error_msg = str(exc_info.value)
        assert 'Available drums:' in error_msg
        assert 'kick' in error_msg
        assert 'snare' in error_msg
    
    def test_aliases(self):
        """Should support drum name aliases."""
        # 'hat' and 'hihat' should map to same note
        assert get_drum_midi_note('hat') == get_drum_midi_note('hihat')
        assert get_drum_midi_note('hat') == 42


class TestIsPercussionInstrument:
    """Tests for is_percussion_instrument function."""
    
    def test_drums_is_percussion(self):
        """'drums' should be recognized as percussion."""
        assert is_percussion_instrument('drums') is True
    
    def test_percussion_is_percussion(self):
        """'percussion' should be recognized as percussion."""
        assert is_percussion_instrument('percussion') is True
    
    def test_kit_is_percussion(self):
        """'kit' should be recognized as percussion."""
        assert is_percussion_instrument('kit') is True
    
    def test_drumkit_is_percussion(self):
        """'drumkit' should be recognized as percussion."""
        assert is_percussion_instrument('drumkit') is True
    
    def test_case_insensitive(self):
        """Should work with any case."""
        assert is_percussion_instrument('DRUMS') is True
        assert is_percussion_instrument('Percussion') is True
        assert is_percussion_instrument('DrumKit') is True
    
    def test_piano_not_percussion(self):
        """'piano' should not be percussion."""
        assert is_percussion_instrument('piano') is False
    
    def test_guitar_not_percussion(self):
        """'guitar' should not be percussion."""
        assert is_percussion_instrument('guitar') is False
    
    def test_violin_not_percussion(self):
        """'violin' should not be percussion."""
        assert is_percussion_instrument('violin') is False
    
    def test_empty_string_not_percussion(self):
        """Empty string should not be percussion."""
        assert is_percussion_instrument('') is False
    
    def test_other_instruments_not_percussion(self):
        """Various melodic instruments should not be percussion."""
        non_percussion = ['bass', 'flute', 'trumpet', 'saxophone', 'organ']
        for instrument in non_percussion:
            assert is_percussion_instrument(instrument) is False


class TestGetAllDrumNames:
    """Tests for get_all_drum_names function."""
    
    def test_returns_list(self):
        """Should return a list."""
        result = get_all_drum_names()
        assert isinstance(result, list)
    
    def test_list_not_empty(self):
        """Should return a non-empty list."""
        result = get_all_drum_names()
        assert len(result) > 0
    
    def test_contains_basic_drums(self):
        """Should include basic drum names."""
        drums = get_all_drum_names()
        assert 'kick' in drums
        assert 'snare' in drums
        assert 'hat' in drums
        assert 'crash' in drums
    
    def test_is_sorted(self):
        """Should return a sorted list."""
        drums = get_all_drum_names()
        assert drums == sorted(drums)
    
    def test_all_drums_are_strings(self):
        """All items should be strings."""
        drums = get_all_drum_names()
        for drum in drums:
            assert isinstance(drum, str)
    
    def test_matches_drum_map_keys(self):
        """Should contain exactly the keys from DRUM_MAP."""
        drums = get_all_drum_names()
        assert set(drums) == set(DRUM_MAP.keys())


class TestValidateDrumName:
    """Tests for validate_drum_name function."""
    
    def test_valid_drums_return_true(self):
        """Valid drum names should return True."""
        assert validate_drum_name('kick') is True
        assert validate_drum_name('snare') is True
        assert validate_drum_name('hat') is True
        assert validate_drum_name('crash') is True
    
    def test_invalid_drums_return_false(self):
        """Invalid drum names should return False."""
        assert validate_drum_name('invalid') is False
        assert validate_drum_name('notadrum') is False
        assert validate_drum_name('xyz') is False
    
    def test_case_insensitive(self):
        """Should work with any case."""
        assert validate_drum_name('KICK') is True
        assert validate_drum_name('Snare') is True
        assert validate_drum_name('HaT') is True
    
    def test_empty_string_invalid(self):
        """Empty string should be invalid."""
        assert validate_drum_name('') is False
    
    def test_all_drum_map_keys_valid(self):
        """All keys in DRUM_MAP should validate."""
        for drum_name in DRUM_MAP.keys():
            assert validate_drum_name(drum_name) is True


class TestDrumMapCompleteness:
    """Integration tests for drum mapping completeness."""
    
    def test_all_gm_drums_covered(self):
        """Should cover all commonly used General MIDI drums."""
        # Core drum kit
        required_drums = [
            'kick', 'snare', 'hat', 'openhat',
            'crash', 'ride',
            'tom1', 'tom2', 'tom3',
            'rimshot', 'clap',
        ]
        
        for drum in required_drums:
            assert drum in DRUM_MAP, f"Missing required drum: {drum}"
            midi_note = get_drum_midi_note(drum)
            assert isinstance(midi_note, int)
            assert 0 <= midi_note <= 127
    
    def test_extended_percussion_covered(self):
        """Should include extended percussion instruments."""
        extended = ['cowbell', 'tambourine', 'woodblock', 'triangle']
        
        for drum in extended:
            assert drum in DRUM_MAP, f"Missing extended percussion: {drum}"
    
    def test_latin_percussion_covered(self):
        """Should include Latin percussion instruments."""
        latin = ['bongo', 'conga', 'timbale', 'maracas']
        
        for drum in latin:
            assert drum in DRUM_MAP, f"Missing Latin percussion: {drum}"
    
    def test_no_duplicate_names(self):
        """Drum names should be unique (except intentional aliases)."""
        # This is automatically true since DRUM_MAP is a dict
        # But we check aliases map to same value
        assert get_drum_midi_note('hat') == get_drum_midi_note('hihat')


class TestDrumMapUsage:
    """Integration tests simulating real usage."""
    
    def test_build_drum_pattern(self):
        """Should be able to build a typical drum pattern."""
        pattern = [
            ('kick', 4),
            ('snare', 4),
            ('hat', 8),
            ('hat', 8),
        ]
        
        midi_notes = []
        for drum, duration in pattern:
            midi_note = get_drum_midi_note(drum)
            midi_notes.append((midi_note, duration))
        
        assert len(midi_notes) == 4
        assert midi_notes[0][0] == 36  # kick
        assert midi_notes[1][0] == 38  # snare
        assert midi_notes[2][0] == 42  # hat
        assert midi_notes[3][0] == 42  # hat
    
    def test_check_instrument_before_drum_lookup(self):
        """Should check if instrument is percussion before drum lookup."""
        instrument = 'drums'
        
        if is_percussion_instrument(instrument):
            # Safe to use drum names
            midi_note = get_drum_midi_note('kick')
            assert midi_note == 36
        else:
            # Would use pitched note parsing instead
            pass
    
    def test_list_available_drums_for_user(self):
        """Should be able to list drums for user documentation."""
        all_drums = get_all_drum_names()
        
        # User could display this as help text
        assert len(all_drums) > 20  # Should have decent coverage
        assert all(isinstance(d, str) for d in all_drums)
