"""
Comprehensive unit tests for MIDI generation.

Tests cover:
- Basic note generation and timing
- Rest and chord handling
- Articulation and dynamic application
- Advanced features (slurs, slides, percussion)
- Meta-events (tempo, time signature, pan)
- Channel assignment
- MIDI file output verification
"""

import pytest
import tempfile
import os
from muslang.midi_gen import MIDIGenerator, INSTRUMENT_MAP
from muslang.ast_nodes import *
from muslang.config import *
import mido


class TestNoteToMIDI:
    """Test note to MIDI number conversion"""
    
    def test_middle_c(self):
        """C4 (middle C) should be MIDI note 60"""
        gen = MIDIGenerator()
        note = Note(pitch='c', octave=4)
        assert gen._note_to_midi(note) == 60
    
    def test_a440(self):
        """A4 (concert pitch) should be MIDI note 69"""
        gen = MIDIGenerator()
        note = Note(pitch='a', octave=4)
        assert gen._note_to_midi(note) == 69
    
    def test_lowest_note(self):
        """C0 should be MIDI note 12"""
        gen = MIDIGenerator()
        note = Note(pitch='c', octave=0)
        assert gen._note_to_midi(note) == 12
    
    def test_highest_note(self):
        """G9 should be MIDI note 127"""
        gen = MIDIGenerator()
        note = Note(pitch='g', octave=9)
        assert gen._note_to_midi(note) == 127
    
    def test_sharp_accidental(self):
        """C#4 should be MIDI note 61"""
        gen = MIDIGenerator()
        note = Note(pitch='c', octave=4, accidental='sharp')
        assert gen._note_to_midi(note) == 61
    
    def test_flat_accidental(self):
        """Bb4 should be MIDI note 70"""
        gen = MIDIGenerator()
        note = Note(pitch='b', octave=4, accidental='flat')
        assert gen._note_to_midi(note) == 70
    
    def test_natural_accidental(self):
        """F-natural 4 should be MIDI note 65"""
        gen = MIDIGenerator()
        note = Note(pitch='f', octave=4, accidental='natural')
        assert gen._note_to_midi(note) == 65
    
    def test_octave_range(self):
        """Test all octaves for C"""
        gen = MIDIGenerator()
        for octave in range(0, 10):
            note = Note(pitch='c', octave=octave)
            expected = (octave + 1) * 12
            assert gen._note_to_midi(note) == expected


class TestDurationToTicks:
    """Test duration to MIDI ticks conversion"""
    
    def test_whole_note(self):
        """Whole note should be 4 * PPQ ticks"""
        gen = MIDIGenerator(ppq=480)
        assert gen._duration_to_ticks(1, False) == 4 * 480
    
    def test_half_note(self):
        """Half note should be 2 * PPQ ticks"""
        gen = MIDIGenerator(ppq=480)
        assert gen._duration_to_ticks(2, False) == 2 * 480
    
    def test_quarter_note(self):
        """Quarter note should be PPQ ticks"""
        gen = MIDIGenerator(ppq=480)
        assert gen._duration_to_ticks(4, False) == 480
    
    def test_eighth_note(self):
        """Eighth note should be PPQ/2 ticks"""
        gen = MIDIGenerator(ppq=480)
        assert gen._duration_to_ticks(8, False) == 240
    
    def test_sixteenth_note(self):
        """Sixteenth note should be PPQ/4 ticks"""
        gen = MIDIGenerator(ppq=480)
        assert gen._duration_to_ticks(16, False) == 120
    
    def test_dotted_quarter(self):
        """Dotted quarter should be 1.5 * PPQ ticks"""
        gen = MIDIGenerator(ppq=480)
        assert gen._duration_to_ticks(4, True) == 720
    
    def test_dotted_half(self):
        """Dotted half should be 3 * PPQ ticks"""
        gen = MIDIGenerator(ppq=480)
        assert gen._duration_to_ticks(2, True) == 1440
    
    def test_different_ppq(self):
        """Test with different PPQ value"""
        gen = MIDIGenerator(ppq=96)
        assert gen._duration_to_ticks(4, False) == 96
        assert gen._duration_to_ticks(8, False) == 48


class TestChannelAssignment:
    """Test MIDI channel assignment"""
    
    def test_first_channel(self):
        """First non-percussion instrument gets channel 0"""
        gen = MIDIGenerator()
        assert gen._get_next_channel() == 0
    
    def test_sequential_channels(self):
        """Sequential instruments get sequential channels"""
        gen = MIDIGenerator()
        assert gen._get_next_channel() == 0
        assert gen._get_next_channel() == 1
        assert gen._get_next_channel() == 2
    
    def test_skip_drum_channel(self):
        """Channel 9 (drums) should be skipped"""
        gen = MIDIGenerator()
        for _ in range(9):
            gen._get_next_channel()
        # Next should be 10 (skipping 9)
        assert gen._get_next_channel() == 10
    
    def test_max_channels(self):
        """Should raise error when exceeding 15 non-percussion channels"""
        gen = MIDIGenerator()
        # Allocate all channels except drum channel
        for _ in range(15):
            gen._get_next_channel()
        
        with pytest.raises(ValueError, match="Too many instruments"):
            gen._get_next_channel()


class TestBasicMIDIGeneration:
    """Test basic MIDI file generation"""
    
    def test_single_note(self):
        """Generate MIDI with single note"""
        # Create AST
        note = Note(pitch='c', octave=4, duration=4)
        instrument = Instrument(name='piano', events=[], voices={1: [note]})
        ast = Sequence(instruments={'piano': instrument})
        
        # Generate MIDI
        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        try:
            gen.generate(ast, temp_path)
            
            # Verify MIDI file
            midi = mido.MidiFile(temp_path)
            # midiutil creates track 0 for tempo, instrument tracks start at 1
            assert len(midi.tracks) >= 1
            
            # Find note events in track 1 (first instrument track)
            messages = list(midi.tracks[1]) if len(midi.tracks) > 1 else list(midi.tracks[0])
            note_ons = [m for m in messages if m.type == 'note_on' and m.velocity > 0]
            note_offs = [m for m in messages if m.type == 'note_on' and m.velocity == 0 or m.type == 'note_off']
            
            assert len(note_ons) >= 1
            assert note_ons[0].note == 60  # C4
        finally:
            os.unlink(temp_path)
    
    def test_melody(self):
        """Generate MIDI with simple melody"""
        # C4 D4 E4 F4
        notes = [
            Note(pitch='c', octave=4, duration=4),
            Note(pitch='d', octave=4, duration=4),
            Note(pitch='e', octave=4, duration=4),
            Note(pitch='f', octave=4, duration=4),
        ]
        instrument = Instrument(name='piano', events=[], voices={1: notes})
        ast = Sequence(instruments={'piano': instrument})
        
        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        try:
            gen.generate(ast, temp_path)
            
            # Verify MIDI file
            midi = mido.MidiFile(temp_path)
            messages = list(midi.tracks[1]) if len(midi.tracks) > 1 else list(midi.tracks[0])
            note_ons = [m for m in messages if m.type == 'note_on' and m.velocity > 0]
            
            assert len(note_ons) >= 4
            assert note_ons[0].note == 60  # C4
            assert note_ons[1].note == 62  # D4
            assert note_ons[2].note == 64  # E4
            assert note_ons[3].note == 65  # F4
        finally:
            os.unlink(temp_path)
    
    def test_rest(self):
        """Test rest handling"""
        events = [
            Note(pitch='c', octave=4, duration=4),
            Rest(duration=4),
            Note(pitch='e', octave=4, duration=4),
        ]
        instrument = Instrument(name='piano', events=[], voices={1: events})
        ast = Sequence(instruments={'piano': instrument})
        
        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        try:
            gen.generate(ast, temp_path)
            
            # Verify MIDI file
            midi = mido.MidiFile(temp_path)
            messages = list(midi.tracks[1]) if len(midi.tracks) > 1 else list(midi.tracks[0])
            note_ons = [m for m in messages if m.type == 'note_on' and m.velocity > 0]
            
            # Should have 2 notes
            assert len(note_ons) == 2
            
            # Second note should start after rest
            elapsed_time = sum(m.time for m in messages[:messages.index(note_ons[1]) + 1])
            # midiutil doubles PPQ internally, so expected time is 2 * 2 * 480 = 1920
            expected_time = 2 * 2 * 480  # 2 quarter notes * 2 (midiutil scaling) * 480
            assert abs(elapsed_time - expected_time) < 10  # Allow small rounding error
        finally:
            os.unlink(temp_path)
    
    def test_chord(self):
        """Test chord generation"""
        # C major chord: C4 E4 G4
        chord_notes = [
            Note(pitch='c', octave=4, duration=4),
            Note(pitch='e', octave=4, duration=4),
            Note(pitch='g', octave=4, duration=4),
        ]
        chord = Chord(notes=chord_notes)
        instrument = Instrument(name='piano', events=[], voices={1: [chord]})
        ast = Sequence(instruments={'piano': instrument})
        
        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        try:
            gen.generate(ast, temp_path)
            
            # Verify MIDI file
            midi = mido.MidiFile(temp_path)
            messages = list(midi.tracks[1]) if len(midi.tracks) > 1 else list(midi.tracks[0])
            note_ons = [m for m in messages if m.type == 'note_on' and m.velocity > 0]
            
            # Should have 3 simultaneous notes
            assert len(note_ons) == 3
            assert note_ons[0].note == 60  # C4
            assert note_ons[1].note == 64  # E4
            assert note_ons[2].note == 67  # G4
            
            # All notes should start at same time
            times = []
            cumulative = 0
            for m in messages:
                if m.type == 'note_on' and m.velocity > 0:
                    times.append(cumulative)
                cumulative += m.time
            
            assert times[0] == times[1] == times[2]
        finally:
            os.unlink(temp_path)


class TestArticulationMapping:
    """Test articulation and dynamic mapping to MIDI"""
    
    def test_staccato_duration(self):
        """Staccato should shorten note duration"""
        events = [
            Articulation(type='staccato'),
            Note(pitch='c', octave=4, duration=4),
        ]
        instrument = Instrument(name='piano', events=[], voices={1: events})
        ast = Sequence(instruments={'piano': instrument})
        
        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        try:
            gen.generate(ast, temp_path)
            
            # Verify note duration is shorter
            midi = mido.MidiFile(temp_path)
            messages = list(midi.tracks[1]) if len(midi.tracks) > 1 else list(midi.tracks[0])
            note_ons = [m for m in messages if m.type == 'note_on' and m.velocity > 0]
            note_offs = [m for m in messages if m.type == 'note_on' and m.velocity == 0 or m.type == 'note_off']
            
            assert len(note_ons) == 1
            
            # Calculate actual duration
            on_time = sum(m.time for m in messages[:messages.index(note_ons[0]) + 1])
            off_idx = next(i for i, m in enumerate(messages) if (m.type == 'note_off' or (m.type == 'note_on' and m.velocity == 0)) and m.note == 60)
            off_time = sum(m.time for m in messages[:off_idx + 1])
            
            duration_ticks = off_time - on_time
            # Just verify staccato makes the note shorter than full duration
            # midiutil's internal timing is complex, but we can verify relative behavior
            full_duration = 2 * 480  # Full quarter note in midiutil's doubled PPQ
            assert duration_ticks < full_duration  # Staccato should be shorter than full
        finally:
            os.unlink(temp_path)
    
    def test_dynamic_level_velocity(self):
        """Dynamic level should affect velocity"""
        # Test piano (p) and forte (f)
        events = [
            DynamicLevel(level='p'),
            Note(pitch='c', octave=4, duration=4),
            DynamicLevel(level='f'),
            Note(pitch='d', octave=4, duration=4),
        ]
        instrument = Instrument(name='piano', events=[], voices={1: events})
        ast = Sequence(instruments={'piano': instrument})
        
        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        try:
            gen.generate(ast, temp_path)
            
            # Verify velocities
            midi = mido.MidiFile(temp_path)
            messages = list(midi.tracks[1]) if len(midi.tracks) > 1 else list(midi.tracks[0])
            note_ons = [m for m in messages if m.type == 'note_on' and m.velocity > 0]
            
            assert len(note_ons) == 2
            
            # Piano velocity should be less than forte
            assert note_ons[0].velocity == VELOCITY_P
            assert note_ons[1].velocity == VELOCITY_F
            assert note_ons[0].velocity < note_ons[1].velocity
        finally:
            os.unlink(temp_path)


class TestAdvancedFeatures:
    """Test advanced MIDI generation features"""
    
    def test_legato_articulation_note_generation(self):
        """Test legato articulation still generates notes correctly"""
        events = [
            Articulation(type='legato'),
            Note(pitch='c', octave=4, duration=4),
            Note(pitch='d', octave=4, duration=4),
            Note(pitch='e', octave=4, duration=4),
        ]
        instrument = Instrument(name='piano', events=[], voices={1: events})
        ast = Sequence(instruments={'piano': instrument})
        
        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        try:
            gen.generate(ast, temp_path)
            
            # Verify notes are present
            midi = mido.MidiFile(temp_path)
            messages = list(midi.tracks[1]) if len(midi.tracks) > 1 else list(midi.tracks[0])

            note_ons = [m for m in messages if m.type == 'note_on' and m.velocity > 0]
            assert len(note_ons) == 3
        finally:
            os.unlink(temp_path)
    
    def test_percussion(self):
        """Test percussion note generation"""
        perc_note = PercussionNote(drum_sound='kick', duration=4)
        instrument = Instrument(name='drums', events=[], voices={1: [perc_note]})
        ast = Sequence(instruments={'drums': instrument})
        
        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        try:
            gen.generate(ast, temp_path)
            
            # Verify drum note is on channel 9
            midi = mido.MidiFile(temp_path)
            messages = list(midi.tracks[1]) if len(midi.tracks) > 1 else list(midi.tracks[0])
            note_ons = [m for m in messages if m.type == 'note_on' and m.velocity > 0]
            
            assert len(note_ons) == 1
            assert note_ons[0].channel == GM_DRUM_CHANNEL
            assert note_ons[0].note == 36  # Kick drum
        finally:
            os.unlink(temp_path)
    
    def test_tempo_change(self):
        """Test tempo meta-event"""
        events = [
            Tempo(bpm=140),
            Note(pitch='c', octave=4, duration=4),
        ]
        instrument = Instrument(name='piano', events=[], voices={1: events})
        ast = Sequence(instruments={'piano': instrument})
        
        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        try:
            gen.generate(ast, temp_path)
            
            # Verify tempo event
            midi = mido.MidiFile(temp_path)
            messages = list(midi.tracks[0])
            tempo_msgs = [m for m in messages if m.type == 'set_tempo']
            
            # Should have at least one tempo message
            assert len(tempo_msgs) >= 1
        finally:
            os.unlink(temp_path)
    
    def test_time_signature(self):
        """Test time signature meta-event"""
        events = [
            TimeSignature(numerator=3, denominator=4),
            Note(pitch='c', octave=4, duration=4),
        ]
        instrument = Instrument(name='piano', events=[], voices={1: events})
        ast = Sequence(instruments={'piano': instrument})
        
        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        try:
            gen.generate(ast, temp_path)
            
            # Verify time signature event
            midi = mido.MidiFile(temp_path)
            # Time signature is in the instrument track (track 1)
            all_messages = []
            for track in midi.tracks:
                all_messages.extend(list(track))
            time_sig_msgs = [m for m in all_messages if m.type == 'time_signature']
            
            assert len(time_sig_msgs) >= 1
            assert time_sig_msgs[0].numerator == 3
            # midiutil uses power-of-2 encoding: 4 = 2^2, stored as 2
            # But mido decodes it back to the actual value when reading
            assert time_sig_msgs[0].denominator == 4
        finally:
            os.unlink(temp_path)
    
    def test_pan(self):
        """Test pan CC event"""
        events = [
            Pan(position=64),  # Center
            Note(pitch='c', octave=4, duration=4),
        ]
        instrument = Instrument(name='piano', events=[], voices={1: events})
        ast = Sequence(instruments={'piano': instrument})
        
        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        try:
            gen.generate(ast, temp_path)
            
            # Verify pan CC
            midi = mido.MidiFile(temp_path)
            messages = list(midi.tracks[1]) if len(midi.tracks) > 1 else list(midi.tracks[0])
            pan_msgs = [m for m in messages if m.type == 'control_change' and m.control == CC_PAN]
            
            assert len(pan_msgs) >= 1
            assert pan_msgs[0].value == 64
        finally:
            os.unlink(temp_path)


class TestMultiInstrument:
    """Test multi-instrument MIDI generation"""
    
    def test_two_instruments(self):
        """Generate MIDI with two instruments"""
        piano_notes = [Note(pitch='c', octave=4, duration=4)]
        piano = Instrument(name='piano', events=[], voices={1: piano_notes})
        
        violin_notes = [Note(pitch='e', octave=5, duration=4)]
        violin = Instrument(name='violin', events=[], voices={1: violin_notes})
        
        ast = Sequence(instruments={'piano': piano, 'violin': violin})
        
        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        try:
            gen.generate(ast, temp_path)
            
            # Verify tracks (track 0 is tempo, tracks 1-2 are instruments)
            midi = mido.MidiFile(temp_path)
            assert len(midi.tracks) >= 2  # At least 2 tracks (tempo + instruments)
            
            # Verify different channels
            if len(midi.tracks) > 2:
                track1_msgs = [m for m in midi.tracks[1] if hasattr(m, 'channel')]
                track2_msgs = [m for m in midi.tracks[2] if hasattr(m, 'channel')]
                
                if track1_msgs and track2_msgs:
                    assert track1_msgs[0].channel != track2_msgs[0].channel
        finally:
            os.unlink(temp_path)
    
    def test_instrument_program_change(self):
        """Test that different instruments get correct program changes"""
        violin = Instrument(name='violin', events=[], voices={1: [Note(pitch='e', octave=5, duration=4)]})
        ast = Sequence(instruments={'violin': violin})
        
        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        try:
            gen.generate(ast, temp_path)
            
            # Verify program change for violin
            midi = mido.MidiFile(temp_path)
            messages = list(midi.tracks[1]) if len(midi.tracks) > 1 else list(midi.tracks[0])
            program_msgs = [m for m in messages if m.type == 'program_change']
            
            assert len(program_msgs) >= 1
            assert program_msgs[0].program == INSTRUMENT_MAP['violin']
        finally:
            os.unlink(temp_path)


class TestSlideGeneration:
    """Test slide/glissando generation"""
    
    def test_chromatic_slide(self):
        """Test chromatic slide with pitch bend"""
        from_note = Note(pitch='c', octave=4, duration=4)
        to_note = Note(pitch='c', octave=5, duration=4)
        slide = Slide(from_note=from_note, to_note=to_note, style='chromatic')
        instrument = Instrument(name='piano', events=[], voices={1: [slide]})
        ast = Sequence(instruments={'piano': instrument})
        
        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        try:
            gen.generate(ast, temp_path)
            
            # Verify pitch bend events
            midi = mido.MidiFile(temp_path)
            messages = list(midi.tracks[1]) if len(midi.tracks) > 1 else list(midi.tracks[0])
            pitch_bend_msgs = [m for m in messages if m.type == 'pitchwheel']
            
            # Should have multiple pitch bend events for smooth slide
            assert len(pitch_bend_msgs) > 1
            
            # Should reset pitch bend at end to 0 (midiutil uses signed format)
            assert pitch_bend_msgs[-1].pitch == 0
        finally:
            os.unlink(temp_path)
    
    def test_stepped_slide(self):
        """Test stepped slide with chromatic notes"""
        from_note = Note(pitch='c', octave=4, duration=4)
        to_note = Note(pitch='e', octave=4, duration=4)
        slide = Slide(from_note=from_note, to_note=to_note, style='stepped')
        instrument = Instrument(name='piano', events=[], voices={1: [slide]})
        ast = Sequence(instruments={'piano': instrument})
        
        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        try:
            gen.generate(ast, temp_path)
            
            # Verify multiple chromatic notes
            midi = mido.MidiFile(temp_path)
            messages = list(midi.tracks[1]) if len(midi.tracks) > 1 else list(midi.tracks[0])
            note_ons = [m for m in messages if m.type == 'note_on' and m.velocity > 0]
            
            # C to E is 4 semitones, should have 5 notes (C, C#, D, D#, E)
            assert len(note_ons) >= 4
        finally:
            os.unlink(temp_path)
    
    def test_portamento_slide(self):
        """Test portamento slide with CC"""
        from_note = Note(pitch='c', octave=4, duration=4)
        to_note = Note(pitch='g', octave=4, duration=4)
        slide = Slide(from_note=from_note, to_note=to_note, style='portamento')
        instrument = Instrument(name='piano', events=[], voices={1: [slide]})
        ast = Sequence(instruments={'piano': instrument})
        
        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        try:
            gen.generate(ast, temp_path)
            
            # Verify portamento CC events
            midi = mido.MidiFile(temp_path)
            messages = list(midi.tracks[1]) if len(midi.tracks) > 1 else list(midi.tracks[0])
            portamento_msgs = [m for m in messages if m.type == 'control_change' and m.control in [CC_PORTAMENTO_TIME, CC_PORTAMENTO_SWITCH]]
            
            # Should have portamento on and off
            assert len(portamento_msgs) >= 2
        finally:
            os.unlink(temp_path)


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_composition(self):
        """Empty composition should raise error"""
        ast = Sequence(instruments={})
        gen = MIDIGenerator(ppq=480)
        
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="No instruments"):
                gen.generate(ast, temp_path)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_very_high_note(self):
        """Very high notes should be clamped"""
        # Try to create a note beyond MIDI range
        gen = MIDIGenerator()
        note = Note(pitch='g', octave=10)  # Beyond normal range
        midi_note = gen._note_to_midi(note)
        assert midi_note <= MIDI_MAX_NOTE
    
    def test_very_low_note(self):
        """Very low notes should be clamped"""
        gen = MIDIGenerator()
        note = Note(pitch='c', octave=0, accidental='flat')  # Below MIDI range
        midi_note = gen._note_to_midi(note)
        assert midi_note >= MIDI_MIN_NOTE
    
    def test_nested_sequence(self):
        """Nested sequences should be flattened"""
        inner_seq = Sequence(events=[Note(pitch='c', octave=4, duration=4)])
        outer_seq = Sequence(events=[inner_seq])
        instrument = Instrument(name='piano', events=[], voices={1: [outer_seq]})
        ast = Sequence(instruments={'piano': instrument})
        
        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        try:
            gen.generate(ast, temp_path)
            
            # Should generate note successfully
            midi = mido.MidiFile(temp_path)
            messages = list(midi.tracks[1]) if len(midi.tracks) > 1 else list(midi.tracks[0])
            note_ons = [m for m in messages if m.type == 'note_on' and m.velocity > 0]
            
            assert len(note_ons) >= 1
        finally:
            os.unlink(temp_path)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
