"""
Tests for timing calculation and state tracking in semantic analysis.
"""

import pytest
from muslang.ast_nodes import *
from muslang.semantics import SemanticAnalyzer, SemanticError
from muslang.config import *


class TestTimingCalculation:
    """Tests for _calculate_timing method"""
    
    def test_simple_note_timing(self):
        """Test timing calculation for a simple note"""
        analyzer = SemanticAnalyzer()
        
        note = Note(pitch='c', octave=4, duration=4, dotted=False)
        instrument = Instrument(name='piano', events=[], voices={1: [note]})
        seq = Sequence(events=[instrument])
        
        result = analyzer._calculate_timing(seq)
        
        # Check that note has timing information
        processed_note = result.events[0].voices[1][0]
        assert processed_note.start_time == 0.0
        assert processed_note.end_time == DEFAULT_MIDI_PPQ  # Quarter note = 1 * PPQ
    
    def test_multiple_notes_timing(self):
        """Test timing for sequential notes"""
        analyzer = SemanticAnalyzer()
        
        notes = [
            Note(pitch='c', octave=4, duration=4),  # Quarter note
            Note(pitch='d', octave=4, duration=4),  # Quarter note
            Note(pitch='e', octave=4, duration=2),  # Half note
        ]
        instrument = Instrument(name='piano', events=[], voices={1: notes})
        seq = Sequence(events=[instrument])
        
        result = analyzer._calculate_timing(seq)
        
        processed_notes = result.events[0].voices[1]
        
        # First note: 0 to PPQ
        assert processed_notes[0].start_time == 0.0
        assert processed_notes[0].end_time == DEFAULT_MIDI_PPQ
        
        # Second note: PPQ to 2*PPQ
        assert processed_notes[1].start_time == DEFAULT_MIDI_PPQ
        assert processed_notes[1].end_time == 2 * DEFAULT_MIDI_PPQ
        
        # Third note (half): 2*PPQ to 4*PPQ
        assert processed_notes[2].start_time == 2 * DEFAULT_MIDI_PPQ
        assert processed_notes[2].end_time == 4 * DEFAULT_MIDI_PPQ
    
    def test_dotted_note_timing(self):
        """Test timing for dotted notes"""
        analyzer = SemanticAnalyzer()
        
        note = Note(pitch='c', octave=4, duration=4, dotted=True)
        instrument = Instrument(name='piano', events=[], voices={1: [note]})
        seq = Sequence(events=[instrument])
        
        result = analyzer._calculate_timing(seq)
        
        processed_note = result.events[0].voices[1][0]
        expected_duration = DEFAULT_MIDI_PPQ * 1.5  # Dotted quarter = 1.5 * quarter
        
        assert processed_note.start_time == 0.0
        assert processed_note.end_time == expected_duration
    
    def test_rest_timing(self):
        """Test timing for rests"""
        analyzer = SemanticAnalyzer()
        
        events = [
            Note(pitch='c', octave=4, duration=4),
            Rest(duration=4),
            Note(pitch='d', octave=4, duration=4),
        ]
        instrument = Instrument(name='piano', events=[], voices={1: events})
        seq = Sequence(events=[instrument])
        
        result = analyzer._calculate_timing(seq)
        
        processed_events = result.events[0].voices[1]
        
        # First note: 0 to PPQ
        assert processed_events[0].start_time == 0.0
        
        # Rest: PPQ to 2*PPQ
        assert processed_events[1].start_time == DEFAULT_MIDI_PPQ
        assert processed_events[1].end_time == 2 * DEFAULT_MIDI_PPQ
        
        # Second note: 2*PPQ to 3*PPQ (after rest)
        assert processed_events[2].start_time == 2 * DEFAULT_MIDI_PPQ
    
    def test_chord_timing(self):
        """Test timing for chords"""
        analyzer = SemanticAnalyzer()
        
        chord_notes = [
            Note(pitch='c', octave=4, duration=4),
            Note(pitch='e', octave=4, duration=4),
            Note(pitch='g', octave=4, duration=4),
        ]
        chord = Chord(notes=chord_notes)
        instrument = Instrument(name='piano', events=[], voices={1: [chord]})
        seq = Sequence(events=[instrument])
        
        result = analyzer._calculate_timing(seq)
        
        processed_chord = result.events[0].voices[1][0]
        
        # All notes in chord should start at same time
        for note in processed_chord.notes:
            assert note.start_time == 0.0
            assert note.end_time == DEFAULT_MIDI_PPQ
        
        # Chord itself should have timing
        assert processed_chord.start_time == 0.0
        assert processed_chord.end_time == DEFAULT_MIDI_PPQ
    
    def test_tuplet_timing(self):
        """Test timing for tuplets (triplets)"""
        analyzer = SemanticAnalyzer()
        
        tuplet_notes = [
            Note(pitch='c', octave=4, duration=8),
            Note(pitch='d', octave=4, duration=8),
            Note(pitch='e', octave=4, duration=8),
        ]
        tuplet = Tuplet(notes=tuplet_notes, ratio=3, actual_duration=2)
        instrument = Instrument(name='piano', events=[], voices={1: [tuplet]})
        seq = Sequence(events=[instrument])
        
        result = analyzer._calculate_timing(seq)
        
        processed_tuplet = result.events[0].voices[1][0]
        
        # Tuplet should fit 3 notes into space of half note (2*PPQ)
        expected_per_note = (2 * DEFAULT_MIDI_PPQ) / 3
        
        assert processed_tuplet.notes[0].start_time == 0.0
        assert abs(processed_tuplet.notes[0].end_time - expected_per_note) < 0.01
        
        assert abs(processed_tuplet.notes[1].start_time - expected_per_note) < 0.01
        assert abs(processed_tuplet.notes[1].end_time - 2 * expected_per_note) < 0.01
        
        assert abs(processed_tuplet.notes[2].start_time - 2 * expected_per_note) < 0.01
        assert abs(processed_tuplet.notes[2].end_time - 3 * expected_per_note) < 0.01
    
    def test_grace_note_timing(self):
        """Test timing for grace notes"""
        analyzer = SemanticAnalyzer()
        
        grace_note = Note(pitch='c', octave=4, duration=16)
        grace = GraceNote(note=grace_note)
        main_note = Note(pitch='d', octave=4, duration=4)
        
        instrument = Instrument(name='piano', events=[], voices={1: [grace, main_note]})
        seq = Sequence(events=[instrument])
        
        result = analyzer._calculate_timing(seq)
        
        processed_grace = result.events[0].voices[1][0]
        processed_main = result.events[0].voices[1][1]
        
        # Grace note should have small duration
        grace_duration = DEFAULT_MIDI_PPQ * GRACE_NOTE_DURATION_RATIO
        assert processed_grace.note.start_time == 0.0
        assert abs(processed_grace.note.end_time - grace_duration) < 0.01
        
        # Main note should start after grace note
        assert abs(processed_main.start_time - grace_duration) < 0.01
    
    def test_legato_note_sequence_timing(self):
        """Test timing for a legato-marked note sequence"""
        analyzer = SemanticAnalyzer()

        events = [
            Articulation(type='legato'),
            Note(pitch='c', octave=4, duration=4),
            Note(pitch='d', octave=4, duration=4),
            Note(pitch='e', octave=4, duration=4),
        ]
        instrument = Instrument(name='piano', events=[], voices={1: events})
        seq = Sequence(events=[instrument])

        result = analyzer._calculate_timing(seq)
        processed_events = result.events[0].voices[1]

        note1 = processed_events[1]
        note2 = processed_events[2]
        note3 = processed_events[3]

        assert note1.start_time == 0.0
        assert note1.end_time == DEFAULT_MIDI_PPQ

        assert note2.start_time == DEFAULT_MIDI_PPQ
        assert note2.end_time == 2 * DEFAULT_MIDI_PPQ

        assert note3.start_time == 2 * DEFAULT_MIDI_PPQ
        assert note3.end_time == 3 * DEFAULT_MIDI_PPQ

    def test_slide_timing_uses_both_note_durations(self):
        """Test slide timing includes both from-note and to-note durations."""
        analyzer = SemanticAnalyzer()

        slide = Slide(
            from_note=Note(pitch='c', octave=4, duration=4),
            to_note=Note(pitch='g', octave=4, duration=4),
            style='chromatic',
        )
        instrument = Instrument(name='piano', events=[], voices={1: [slide]})
        seq = Sequence(events=[instrument])

        result = analyzer._calculate_timing(seq)

        processed_slide = result.events[0].voices[1][0]
        assert processed_slide.from_note.start_time == 0.0
        assert processed_slide.from_note.end_time == DEFAULT_MIDI_PPQ
        assert processed_slide.to_note.start_time == DEFAULT_MIDI_PPQ
        assert processed_slide.to_note.end_time == 2 * DEFAULT_MIDI_PPQ
    
    def test_duration_to_ticks(self):
        """Test _duration_to_ticks helper method"""
        analyzer = SemanticAnalyzer()
        
        # Whole note
        assert analyzer._duration_to_ticks(1, False) == 4 * DEFAULT_MIDI_PPQ
        
        # Half note
        assert analyzer._duration_to_ticks(2, False) == 2 * DEFAULT_MIDI_PPQ
        
        # Quarter note
        assert analyzer._duration_to_ticks(4, False) == DEFAULT_MIDI_PPQ
        
        # Eighth note
        assert analyzer._duration_to_ticks(8, False) == DEFAULT_MIDI_PPQ / 2
        
        # Dotted quarter note
        assert analyzer._duration_to_ticks(4, True) == DEFAULT_MIDI_PPQ * 1.5

    def test_measure_duration_mismatch_includes_instrument_and_line(self):
        """Mismatch errors include instrument and source line context when available."""
        analyzer = SemanticAnalyzer()

        # 3/4 expects 3 quarter notes per measure, but provide 4 quarter notes.
        measure = Measure(
            events=[
                Note(pitch='c', octave=4, duration=4),
                Note(pitch='d', octave=4, duration=4),
                Note(pitch='e', octave=4, duration=4),
                Note(pitch='f', octave=4, duration=4),
            ],
            measure_number=1,
            location=SourceLocation(line=21, column=3),
        )

        instrument = Instrument(
            name='violin',
            events=[],
            voices={1: [TimeSignature(numerator=3, denominator=4), measure]},
        )
        seq = Sequence(events=[instrument])

        with pytest.raises(SemanticError) as exc_info:
            analyzer.analyze(seq)

        error_msg = str(exc_info.value)
        assert "Instrument 'violin'" in error_msg
        assert "line 21" in error_msg
        assert "Measure 1 duration mismatch" in error_msg


class TestStateTracking:
    """Tests for _track_state method"""
    
    def test_default_state(self):
        """Test default articulation and dynamic state"""
        analyzer = SemanticAnalyzer()
        
        note = Note(pitch='c', octave=4, duration=4)
        instrument = Instrument(name='piano', events=[], voices={1: [note]})
        seq = Sequence(events=[instrument])
        
        # Add timing first
        seq = analyzer._calculate_timing(seq)
        result = analyzer._track_state(seq)
        
        processed_note = result.events[0].voices[1][0]
        
        # Default state should be natural articulation and mf dynamic
        assert processed_note.articulation == 'natural'
        assert processed_note.dynamic_level == 'mf'
        assert processed_note.velocity == VELOCITY_MF
    
    def test_articulation_state_tracking(self):
        """Test articulation state persistence"""
        analyzer = SemanticAnalyzer()
        
        events = [
            Articulation(type='staccato'),
            Note(pitch='c', octave=4, duration=4),
            Note(pitch='d', octave=4, duration=4),
            Articulation(type='legato'),
            Note(pitch='e', octave=4, duration=4),
        ]
        instrument = Instrument(name='piano', events=[], voices={1: events})
        seq = Sequence(events=[instrument])
        
        seq = analyzer._calculate_timing(seq)
        result = analyzer._track_state(seq)
        
        processed_events = result.events[0].voices[1]
        
        # First note should have staccato
        assert processed_events[1].articulation == 'staccato'
        
        # Second note should still have staccato
        assert processed_events[2].articulation == 'staccato'
        
        # Third note should have legato
        assert processed_events[4].articulation == 'legato'
    
    def test_dynamic_level_state_tracking(self):
        """Test dynamic level state persistence"""
        analyzer = SemanticAnalyzer()
        
        events = [
            DynamicLevel(level='p'),
            Note(pitch='c', octave=4, duration=4),
            Note(pitch='d', octave=4, duration=4),
            DynamicLevel(level='f'),
            Note(pitch='e', octave=4, duration=4),
        ]
        instrument = Instrument(name='piano', events=[], voices={1: events})
        seq = Sequence(events=[instrument])
        
        seq = analyzer._calculate_timing(seq)
        result = analyzer._track_state(seq)
        
        processed_events = result.events[0].voices[1]
        
        # First note should be piano
        assert processed_events[1].dynamic_level == 'p'
        assert processed_events[1].velocity == VELOCITY_P
        
        # Second note should still be piano
        assert processed_events[2].dynamic_level == 'p'
        assert processed_events[2].velocity == VELOCITY_P
        
        # Third note should be forte
        assert processed_events[4].dynamic_level == 'f'
        assert processed_events[4].velocity == VELOCITY_F
    
    def test_crescendo(self):
        """Test crescendo (gradual increase in volume)"""
        analyzer = SemanticAnalyzer()
        
        events = [
            DynamicLevel(level='p'),
            DynamicTransition(type='crescendo'),
            Note(pitch='c', octave=4, duration=4),
            Note(pitch='d', octave=4, duration=4),
            Note(pitch='e', octave=4, duration=4),
            Note(pitch='f', octave=4, duration=4),
        ]
        instrument = Instrument(name='piano', events=[], voices={1: events})
        seq = Sequence(events=[instrument])
        
        seq = analyzer._calculate_timing(seq)
        result = analyzer._track_state(seq)
        
        processed_events = result.events[0].voices[1]
        
        # Extract notes (skip directive events)
        notes = [e for e in processed_events if isinstance(e, Note)]
        
        # Velocities should increase
        velocities = [n.velocity for n in notes]
        assert velocities[0] < velocities[1]
        assert velocities[1] < velocities[2]
        assert velocities[2] < velocities[3]
    
    def test_diminuendo(self):
        """Test diminuendo (gradual decrease in volume)"""
        analyzer = SemanticAnalyzer()
        
        events = [
            DynamicLevel(level='f'),
            DynamicTransition(type='diminuendo'),
            Note(pitch='c', octave=4, duration=4),
            Note(pitch='d', octave=4, duration=4),
            Note(pitch='e', octave=4, duration=4),
            Note(pitch='f', octave=4, duration=4),
        ]
        instrument = Instrument(name='piano', events=[], voices={1: events})
        seq = Sequence(events=[instrument])
        
        seq = analyzer._calculate_timing(seq)
        result = analyzer._track_state(seq)
        
        processed_events = result.events[0].voices[1]
        
        # Extract notes
        notes = [e for e in processed_events if isinstance(e, Note)]
        
        # Velocities should decrease
        velocities = [n.velocity for n in notes]
        assert velocities[0] > velocities[1]
        assert velocities[1] > velocities[2]
        assert velocities[2] > velocities[3]
    
    def test_reset_articulation(self):
        """Test reset to natural articulation"""
        analyzer = SemanticAnalyzer()
        
        events = [
            Articulation(type='staccato'),
            Note(pitch='c', octave=4, duration=4),
            Reset(type='natural'),
            Note(pitch='d', octave=4, duration=4),
        ]
        instrument = Instrument(name='piano', events=[], voices={1: events})
        seq = Sequence(events=[instrument])
        
        seq = analyzer._calculate_timing(seq)
        result = analyzer._track_state(seq)
        
        processed_events = result.events[0].voices[1]
        
        # First note should be staccato
        assert processed_events[1].articulation == 'staccato'
        
        # Second note should be natural (after reset)
        assert processed_events[3].articulation == 'natural'
    
    def test_reset_full(self):
        """Test full reset (articulation and dynamics)"""
        analyzer = SemanticAnalyzer()
        
        events = [
            Articulation(type='staccato'),
            DynamicLevel(level='ff'),
            Note(pitch='c', octave=4, duration=4),
            Reset(type='full'),
            Note(pitch='d', octave=4, duration=4),
        ]
        instrument = Instrument(name='piano', events=[], voices={1: events})
        seq = Sequence(events=[instrument])
        
        seq = analyzer._calculate_timing(seq)
        result = analyzer._track_state(seq)
        
        processed_events = result.events[0].voices[1]
        
        # First note should be staccato and ff
        assert processed_events[2].articulation == 'staccato'
        assert processed_events[2].velocity == VELOCITY_FF
        
        # Second note should be natural and mf (default)
        assert processed_events[4].articulation == 'natural'
        assert processed_events[4].dynamic_level == 'mf'
        assert processed_events[4].velocity == VELOCITY_MF
    
    def test_chord_state_tracking(self):
        """Test state tracking for chords"""
        analyzer = SemanticAnalyzer()
        
        events = [
            Articulation(type='legato'),
            DynamicLevel(level='f'),
            Chord(notes=[
                Note(pitch='c', octave=4, duration=4),
                Note(pitch='e', octave=4, duration=4),
                Note(pitch='g', octave=4, duration=4),
            ]),
        ]
        instrument = Instrument(name='piano', events=[], voices={1: events})
        seq = Sequence(events=[instrument])
        
        seq = analyzer._calculate_timing(seq)
        result = analyzer._track_state(seq)
        
        processed_chord = result.events[0].voices[1][2]
        
        # All notes in chord should have same state
        for note in processed_chord.notes:
            assert note.articulation == 'legato'
            assert note.dynamic_level == 'f'
            assert note.velocity == VELOCITY_F
    
    def test_percussion_velocity(self):
        """Test velocity tracking for percussion"""
        analyzer = SemanticAnalyzer()
        
        events = [
            DynamicLevel(level='ff'),
            PercussionNote(drum_sound='kick', duration=4),
        ]
        instrument = Instrument(name='drums', events=[], voices={1: events})
        seq = Sequence(events=[instrument])
        
        seq = analyzer._calculate_timing(seq)
        result = analyzer._track_state(seq)
        
        processed_perc = result.events[0].voices[1][1]
        
        # Percussion should have velocity assigned
        assert processed_perc.velocity == VELOCITY_FF


class TestIntegratedTimingAndState:
    """Integration tests for timing and state tracking together"""
    
    def test_full_pipeline(self):
        """Test complete semantic analysis pipeline"""
        analyzer = SemanticAnalyzer()
        
        events = [
            DynamicLevel(level='p'),
            Articulation(type='legato'),
            Note(pitch='c', octave=4, duration=4),
            Note(pitch='d', octave=4, duration=8),
            Rest(duration=8),
            Articulation(type='staccato'),
            DynamicLevel(level='f'),
            Note(pitch='e', octave=4, duration=4),
        ]
        # For analyze(), need to wrap in Voice node which _regroup_voices expects
        voice_events = [Voice(number=1, events=[])] + events
        instrument = Instrument(name='piano', events=[], voices={1: voice_events})
        seq = Sequence(events=[instrument])
        
        # Run full analysis
        result = analyzer.analyze(seq)
        
        processed_events = result.events[0].voices[1]
        
        # Extract only notes and rests (filter out directives)
        notes_and_rests = [e for e in processed_events if isinstance(e, (Note, Rest))]
        
        note1 = notes_and_rests[0]  # First note
        note2 = notes_and_rests[1]  # Second note
        rest = notes_and_rests[2]   # Rest
        note3 = notes_and_rests[3]  # Third note
        
        # Check timing
        assert note1.start_time == 0.0
        assert note1.end_time == DEFAULT_MIDI_PPQ
        
        assert note2.start_time == DEFAULT_MIDI_PPQ
        assert note2.end_time == DEFAULT_MIDI_PPQ * 1.5
        
        assert rest.start_time == DEFAULT_MIDI_PPQ * 1.5
        assert rest.end_time == DEFAULT_MIDI_PPQ * 2.0
        
        assert note3.start_time == DEFAULT_MIDI_PPQ * 2.0
        assert note3.end_time == DEFAULT_MIDI_PPQ * 3.0
        
        # Check state
        assert note1.articulation == 'legato'
        assert note1.dynamic_level == 'p'
        assert note1.velocity == VELOCITY_P
        
        assert note2.articulation == 'legato'
        assert note2.dynamic_level == 'p'
        
        assert note3.articulation == 'staccato'
        assert note3.dynamic_level == 'f'
        assert note3.velocity == VELOCITY_F
    
    def test_multiple_instruments(self):
        """Test timing and state for multiple instruments"""
        analyzer = SemanticAnalyzer()
        
        piano_events = [
            DynamicLevel(level='mf'),
            Note(pitch='c', octave=4, duration=4),
            Note(pitch='d', octave=4, duration=4),
        ]
        
        violin_events = [
            DynamicLevel(level='f'),
            Articulation(type='legato'),
            Note(pitch='e', octave=5, duration=2),
        ]
        
        # For analyze(), need to wrap in Voice nodes which _regroup_voices expects
        piano_voice_events = [Voice(number=1, events=[])] + piano_events
        violin_voice_events = [Voice(number=1, events=[])] + violin_events
        
        seq = Sequence(events=[
            Instrument(name='piano', events=[], voices={1: piano_voice_events}),
            Instrument(name='violin', events=[], voices={1: violin_voice_events}),
        ])
        
        result = analyzer.analyze(seq)
        
        # Check piano timing (independent)
        piano_notes = [e for e in result.events[0].voices[1] if isinstance(e, Note)]
        assert piano_notes[0].start_time == 0.0
        assert piano_notes[0].velocity == VELOCITY_MF
        
        # Check violin timing (independent, also starts at 0)
        violin_notes = [e for e in result.events[1].voices[1] if isinstance(e, Note)]
        assert violin_notes[0].start_time == 0.0
        assert violin_notes[0].velocity == VELOCITY_F
        assert violin_notes[0].articulation == 'legato'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
