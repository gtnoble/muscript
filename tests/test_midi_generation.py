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
from muslang.parser import parse_muslang
from muslang.semantics import SemanticAnalyzer
import mido


class TestNoteToMIDI:
    """Test note to MIDI number conversion"""
    
    def test_middle_c(self):
        """C4 (middle C) should be MIDI note 60"""
        gen = MIDIGenerator()
        note = Note(pitches=[('c', 4, None)])
        assert gen._note_to_midi(note) == 60
    
    def test_a440(self):
        """A4 (concert pitch) should be MIDI note 69"""
        gen = MIDIGenerator()
        note = Note(pitches=[('a', 4, None)])
        assert gen._note_to_midi(note) == 69
    
    def test_lowest_note(self):
        """C0 should be MIDI note 12"""
        gen = MIDIGenerator()
        note = Note(pitches=[('c', 0, None)])
        assert gen._note_to_midi(note) == 12
    
    def test_highest_note(self):
        """G9 should be MIDI note 127"""
        gen = MIDIGenerator()
        note = Note(pitches=[('g', 9, None)])
        assert gen._note_to_midi(note) == 127
    
    def test_sharp_accidental(self):
        """C#4 should be MIDI note 61"""
        gen = MIDIGenerator()
        note = Note(pitches=[('c', 4, 'sharp')])
        assert gen._note_to_midi(note) == 61
    
    def test_flat_accidental(self):
        """Bb4 should be MIDI note 70"""
        gen = MIDIGenerator()
        note = Note(pitches=[('b', 4, 'flat')])
        assert gen._note_to_midi(note) == 70
    
    def test_natural_accidental(self):
        """F-natural 4 should be MIDI note 65"""
        gen = MIDIGenerator()
        note = Note(pitches=[('f', 4, 'natural')])
        assert gen._note_to_midi(note) == 65
    
    def test_octave_range(self):
        """Test all octaves for C"""
        gen = MIDIGenerator()
        for octave in range(0, 10):
            note = Note(pitches=[('c', octave, None)])
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
        note = Note(pitches=[('c', 4, None)], duration=4)
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
            Note(pitches=[('c', 4, None)], duration=4),
            Note(pitches=[('d', 4, None)], duration=4),
            Note(pitches=[('e', 4, None)], duration=4),
            Note(pitches=[('f', 4, None)], duration=4),
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
            Note(pitches=[('c', 4, None)], duration=4),
            Rest(duration=4),
            Note(pitches=[('e', 4, None)], duration=4),
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
        chord = Note(pitches=[('c', 4, None), ('e', 4, None), ('g', 4, None)], duration=4)
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

    def _first_note_duration_ticks(self, midi_path: str) -> int:
        midi = mido.MidiFile(midi_path)
        track = midi.tracks[1] if len(midi.tracks) > 1 else midi.tracks[0]

        abs_time = 0
        timed_msgs = []
        for msg in track:
            abs_time += msg.time
            timed_msgs.append((abs_time, msg))

        note_on_time = None
        note_number = None
        for timestamp, msg in timed_msgs:
            if msg.type == 'note_on' and msg.velocity > 0:
                note_on_time = timestamp
                note_number = msg.note
                break

        assert note_on_time is not None

        for timestamp, msg in timed_msgs:
            is_off = msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0)
            if is_off and msg.note == note_number and timestamp >= note_on_time:
                return timestamp - note_on_time

        raise AssertionError("Could not find note-off for first note")

    def test_articulation_directive_changes_duration(self):
        """Legato and staccato directives should produce different note lengths."""
        staccato_events = [
            Articulation(type='staccato'),
            Note(pitches=[('c', 4, None)], duration=4),
        ]
        legato_events = [
            Articulation(type='legato'),
            Note(pitches=[('c', 4, None)], duration=4),
        ]

        staccato_ast = Sequence(instruments={'piano': Instrument(name='piano', events=[], voices={1: staccato_events})})
        legato_ast = Sequence(instruments={'piano': Instrument(name='piano', events=[], voices={1: legato_events})})

        # Run semantic analysis to apply articulation to notes
        analyzer = SemanticAnalyzer()
        staccato_ast = analyzer.analyze(staccato_ast)
        legato_ast = analyzer.analyze(legato_ast)

        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f1, \
             tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f2:
            staccato_path = f1.name
            legato_path = f2.name

        try:
            gen.generate(staccato_ast, staccato_path)
            gen.generate(legato_ast, legato_path)

            staccato_ticks = self._first_note_duration_ticks(staccato_path)
            legato_ticks = self._first_note_duration_ticks(legato_path)

            assert staccato_ticks < legato_ticks

            ratio = staccato_ticks / legato_ticks
            expected_ratio = STACCATO_DURATION / LEGATO_DURATION
            assert abs(ratio - expected_ratio) < 0.1
        finally:
            os.unlink(staccato_path)
            os.unlink(legato_path)
    
    def test_staccato_duration(self):
        """Staccato should shorten note duration"""
        events = [
            Articulation(type='staccato'),
            Note(pitches=[('c', 4, None)], duration=4),
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
            Note(pitches=[('c', 4, None)], duration=4),
            DynamicLevel(level='f'),
            Note(pitches=[('d', 4, None)], duration=4),
        ]
        instrument = Instrument(name='piano', events=[], voices={1: events})
        ast = Sequence(instruments={'piano': instrument})
        
        # Run semantic analysis to apply dynamics to notes
        analyzer = SemanticAnalyzer()
        ast = analyzer.analyze(ast)
        
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
            Note(pitches=[('c', 4, None)], duration=4),
            Note(pitches=[('d', 4, None)], duration=4),
            Note(pitches=[('e', 4, None)], duration=4),
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


class TestOrnamentMIDI:
    """Test ornament expansion yields audible MIDI note events"""

    @pytest.mark.parametrize(
        "marker,expected_count",
        [
            ("%trill", 8),
            ("%mordent", 3),
            ("%turn", 4),
            ("%tremolo", 4),
        ],
    )
    def test_ornament_generates_expected_note_count(self, marker, expected_count):
        source = f"""
        piano {{
          V1: {marker} c4/4 r/4 r/4 r/4;
        }}
        """

        analyzed = SemanticAnalyzer().analyze(parse_muslang(source))
        gen = MIDIGenerator(ppq=480)

        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name

        try:
            gen.generate(analyzed, temp_path)

            midi = mido.MidiFile(temp_path)
            messages = list(midi.tracks[1]) if len(midi.tracks) > 1 else list(midi.tracks[0])
            note_ons = [m for m in messages if m.type == 'note_on' and m.velocity > 0]
            assert len(note_ons) == expected_count
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
            Note(pitches=[('c', 4, None)], duration=4),
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
            Note(pitches=[('c', 4, None)], duration=4),
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
            Note(pitches=[('c', 4, None)], duration=4),
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

    def test_multiple_voices_use_distinct_channels(self):
        """Voices in the same instrument should use separate channels."""
        source = """
        piano {
          V1: c4/2 r/2;
          V2: c4/2 r/2;
        }
        """
        analyzed = SemanticAnalyzer().analyze(parse_muslang(source))

        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name

        try:
            gen.generate(analyzed, temp_path)

            midi = mido.MidiFile(temp_path)
            messages = list(midi.tracks[1]) if len(midi.tracks) > 1 else list(midi.tracks[0])
            note_ons = [m for m in messages if m.type == 'note_on' and m.velocity > 0]

            assert len(note_ons) == 2
            channels = {m.channel for m in note_ons}
            assert len(channels) == 2
        finally:
            os.unlink(temp_path)
    
    def test_two_instruments(self):
        """Generate MIDI with two instruments"""
        piano_notes = [Note(pitches=[('c', 4, None)], duration=4)]
        piano = Instrument(name='piano', events=[], voices={1: piano_notes})
        
        violin_notes = [Note(pitches=[('e', 5, None)], duration=4)]
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
        violin = Instrument(name='violin', events=[], voices={1: [Note(pitches=[('e', 5, None)], duration=4)]})
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
        from_note = Note(pitches=[('c', 4, None)], duration=4)
        to_note = Note(pitches=[('c', 5, None)], duration=4)
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
        from_note = Note(pitches=[('c', 4, None)], duration=4)
        to_note = Note(pitches=[('e', 4, None)], duration=4)
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
        from_note = Note(pitches=[('c', 4, None)], duration=4)
        to_note = Note(pitches=[('g', 4, None)], duration=4)
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
        note = Note(pitches=[('g', 10, None)])  # Beyond normal range
        midi_note = gen._note_to_midi(note)
        assert midi_note <= MIDI_MAX_NOTE
    
    def test_very_low_note(self):
        """Very low notes should be clamped"""
        gen = MIDIGenerator()
        note = Note(pitches=[('c', 0, 'flat')])  # Below MIDI range
        midi_note = gen._note_to_midi(note)
        assert midi_note >= MIDI_MIN_NOTE
    
    def test_nested_sequence(self):
        """Nested sequences should be flattened"""
        inner_seq = Sequence(events=[Note(pitches=[('c', 4, None)], duration=4)])
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

    def test_unexpanded_ornament_raises_error(self):
        """MIDI generation should fail fast for unexpanded ornament nodes"""
        events = [
            Ornament(type='trill'),
            Note(pitches=[('c', 4, None)], duration=4),
        ]
        instrument = Instrument(name='piano', events=[], voices={1: events})
        ast = Sequence(instruments={'piano': instrument})

        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="Unexpanded ornament"):
                gen.generate(ast, temp_path)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestMetaEventChanges:
    """Tests for multiple tempo, time signature, and key signature changes in MIDI output"""
    
    def test_multiple_time_signature_changes(self):
        """Test multiple time signature changes are written to MIDI"""
        events = [
            TimeSignature(numerator=4, denominator=4),
            Note(pitches=[('c', 4, None)], duration=4),
            TimeSignature(numerator=3, denominator=4),
            Note(pitches=[('d', 4, None)], duration=4),
            TimeSignature(numerator=5, denominator=4),
            Note(pitches=[('e', 4, None)], duration=4),
        ]
        instrument = Instrument(name='piano', events=[], voices={1: events})
        ast = Sequence(instruments={'piano': instrument})
        
        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        try:
            gen.generate(ast, temp_path)
            
            # Verify multiple time signature events
            midi = mido.MidiFile(temp_path)
            all_messages = []
            for track in midi.tracks:
                all_messages.extend(list(track))
            
            time_sig_msgs = [m for m in all_messages if m.type == 'time_signature']
            
            # Should have 3 time signature events
            assert len(time_sig_msgs) >= 3
            
            # Verify the values
            assert time_sig_msgs[0].numerator == 4
            assert time_sig_msgs[0].denominator == 4
            
            assert time_sig_msgs[1].numerator == 3
            assert time_sig_msgs[1].denominator == 4
            
            assert time_sig_msgs[2].numerator == 5
            assert time_sig_msgs[2].denominator == 4
        finally:
            os.unlink(temp_path)
    
    def test_multiple_tempo_changes(self):
        """Test multiple tempo changes are written to MIDI"""
        events = [
            Tempo(bpm=120),
            Note(pitches=[('c', 4, None)], duration=4),
            Tempo(bpm=60),
            Note(pitches=[('d', 4, None)], duration=4),
            Tempo(bpm=180),
            Note(pitches=[('e', 4, None)], duration=4),
        ]
        instrument = Instrument(name='piano', events=[], voices={1: events})
        ast = Sequence(instruments={'piano': instrument})
        
        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        try:
            gen.generate(ast, temp_path)
            
            # Verify multiple tempo events
            midi = mido.MidiFile(temp_path)
            all_messages = []
            for track in midi.tracks:
                all_messages.extend(list(track))
            
            tempo_msgs = [m for m in all_messages if m.type == 'set_tempo']
            
            # Should have at least 3 tempo events (plus potentially default)
            assert len(tempo_msgs) >= 3
            
            # Verify tempo values (mido stores tempo in microseconds per beat)
            # 120 BPM = 500000 microseconds per beat
            # 60 BPM = 1000000 microseconds per beat
            # 180 BPM = 333333 microseconds per beat
            bpm_to_tempo = lambda bpm: int(60000000 / bpm)
            assert any(abs(m.tempo - bpm_to_tempo(120)) < 100 for m in tempo_msgs)
            assert any(abs(m.tempo - bpm_to_tempo(60)) < 100 for m in tempo_msgs)
            assert any(abs(m.tempo - bpm_to_tempo(180)) < 100 for m in tempo_msgs)
        finally:
            os.unlink(temp_path)
    
    def test_time_signature_changes_timing(self):
        """Test that time signature changes occur at the correct times"""
        events = [
            TimeSignature(numerator=4, denominator=4),
            Note(pitches=[('c', 4, None)], duration=4),
            Note(pitches=[('d', 4, None)], duration=4),
            TimeSignature(numerator=3, denominator=4),
            Note(pitches=[('e', 4, None)], duration=4),
        ]
        instrument = Instrument(name='piano', events=[], voices={1: events})
        ast = Sequence(instruments={'piano': instrument})
        
        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        try:
            gen.generate(ast, temp_path)
            
            midi = mido.MidiFile(temp_path)
            all_messages = []
            for track in midi.tracks:
                all_messages.extend(list(track))
            
            time_sig_msgs = [m for m in all_messages if m.type == 'time_signature']
            
            # First time signature should be at time 0
            assert time_sig_msgs[0].time == 0 or sum(m.time for m in all_messages[:all_messages.index(time_sig_msgs[0])+1]) == 0
            
            # Second time signature should be after 2 quarter notes (2 * 480 = 960 ticks)
            # Calculate absolute time for second time signature
            second_ts_idx = all_messages.index(time_sig_msgs[1])
            abs_time_second_ts = sum(m.time for m in all_messages[:second_ts_idx+1])
            
            # Should be approximately after 2 beats
            # Note: The actual timing might vary based on when meta-events are placed
            assert abs_time_second_ts >= 960
        finally:
            os.unlink(temp_path)
    
    def test_tempo_changes_timing(self):
        """Test that tempo changes occur at the correct times"""
        events = [
            Tempo(bpm=120),
            Note(pitches=[('c', 4, None)], duration=4),
            Tempo(bpm=90),
            Note(pitches=[('d', 4, None)], duration=4),
        ]
        instrument = Instrument(name='piano', events=[], voices={1: events})
        ast = Sequence(instruments={'piano': instrument})
        
        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        try:
            gen.generate(ast, temp_path)
            
            midi = mido.MidiFile(temp_path)
            all_messages = []
            for track in midi.tracks:
                all_messages.extend(list(track))
            
            tempo_msgs = [m for m in all_messages if m.type == 'set_tempo']
            
            # Should have at least 2 tempo events
            assert len(tempo_msgs) >= 2
            
            # First tempo should be at time 0
            first_tempo_idx = all_messages.index(tempo_msgs[0])
            abs_time_first = sum(m.time for m in all_messages[:first_tempo_idx+1])
            assert abs_time_first == 0
            
            # Second tempo should be after 1 quarter note
            if len(tempo_msgs) > 1:
                second_tempo_idx = all_messages.index(tempo_msgs[1])
                abs_time_second = sum(m.time for m in all_messages[:second_tempo_idx+1])
                # Should be approximately after 1 beat
                # Note: The actual timing might vary based on when meta-events are placed
                assert abs_time_second >= 480
        finally:
            os.unlink(temp_path)
    
    def test_combined_meta_event_changes(self):
        """Test combinations of tempo and time signature changes"""
        measure1 = Measure(
            events=[
                Note(pitches=[('c', 4, None)], duration=4),
                Note(pitches=[('d', 4, None)], duration=4),
                Note(pitches=[('e', 4, None)], duration=4),
                Note(pitches=[('f', 4, None)], duration=4),
            ],
            measure_number=1,
        )
        
        measure2 = Measure(
            events=[
                Note(pitches=[('g', 4, None)], duration=4),
                Note(pitches=[('a', 4, None)], duration=4),
                Note(pitches=[('b', 4, None)], duration=4),
            ],
            measure_number=2,
        )
        
        events = [
            Tempo(bpm=120),
            TimeSignature(numerator=4, denominator=4),
            measure1,
            Tempo(bpm=90),
            TimeSignature(numerator=3, denominator=4),
            measure2,
        ]
        
        instrument = Instrument(name='piano', events=[], voices={1: events})
        ast = Sequence(instruments={'piano': instrument})
        
        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        try:
            gen.generate(ast, temp_path)
            
            # Verify file is valid and contains both types of events
            midi = mido.MidiFile(temp_path)
            all_messages = []
            for track in midi.tracks:
                all_messages.extend(list(track))
            
            tempo_msgs = [m for m in all_messages if m.type == 'set_tempo']
            time_sig_msgs = [m for m in all_messages if m.type == 'time_signature']
            note_ons = [m for m in all_messages if m.type == 'note_on' and m.velocity > 0]
            
            # Should have tempo changes, time signature changes, and notes
            assert len(tempo_msgs) >= 2
            assert len(time_sig_msgs) >= 2
            assert len(note_ons) == 7  # 4 notes + 3 notes
        finally:
            os.unlink(temp_path)
    
    def test_time_signature_in_measure(self):
        """Test time signature change within a measure context"""
        # Time signature before measure
        measure = Measure(
            events=[
                Note(pitches=[('c', 4, None)], duration=4),
                Note(pitches=[('d', 4, None)], duration=4),
                Note(pitches=[('e', 4, None)], duration=4),
            ],
            measure_number=1,
        )
        
        events = [
            TimeSignature(numerator=3, denominator=4),
            measure,
        ]
        
        instrument = Instrument(name='piano', events=[], voices={1: events})
        ast = Sequence(instruments={'piano': instrument})
        
        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        try:
            gen.generate(ast, temp_path)
            
            # Should generate valid MIDI
            midi = mido.MidiFile(temp_path)
            all_messages = []
            for track in midi.tracks:
                all_messages.extend(list(track))
            
            time_sig_msgs = [m for m in all_messages if m.type == 'time_signature']
            note_ons = [m for m in all_messages if m.type == 'note_on' and m.velocity > 0]
            
            assert len(time_sig_msgs) >= 1
            assert time_sig_msgs[0].numerator == 3
            assert len(note_ons) == 3
        finally:
            os.unlink(temp_path)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
