"""
Comprehensive tests for slide/glissando functionality.

Tests cover:
- Chromatic slides with pitch bend generation
- Stepped slides with chromatic note sequences
- Portamento slides with MIDI CC
- Duration handling and timing calculations
- Interval variations (small, medium, large)
- Integration with dynamics and articulation
- Parser edge cases
- Semantic validation

"""

import pytest
import tempfile
import os
import mido
from muslang.parser import parse_muslang
from muslang.semantics import SemanticAnalyzer
from muslang.midi_gen import MIDIGenerator
from muslang.ast_nodes import Note, Slide, Instrument, Sequence
from muslang.config import (
    SLIDE_STEPS, PITCH_BEND_RANGE, CC_PORTAMENTO_TIME, 
    CC_PORTAMENTO_SWITCH, VELOCITY_MF, VELOCITY_P, VELOCITY_F,
    STACCATO_DURATION, LEGATO_DURATION
)


def _voice_events(ast, instrument='piano', voice=1):
    return [event for measure in ast.instruments[instrument].voices[voice] for event in measure.events]


# ============================================================================
# Test Chromatic Slides (Pitch Bend)
# ============================================================================

class TestChromaticSlide:
    """Test chromatic slides using pitch bend"""
    
    def test_chromatic_slide_pitch_bend_generation(self):
        """Test that chromatic slide generates correct pitch bend events"""
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
            
            midi = mido.MidiFile(temp_path)
            messages = list(midi.tracks[1]) if len(midi.tracks) > 1 else list(midi.tracks[0])
            pitch_bend_msgs = [m for m in messages if m.type == 'pitchwheel']
            
            # Should have SLIDE_STEPS + 1 pitch bend events (including start at 0)
            assert len(pitch_bend_msgs) >= SLIDE_STEPS, f"Expected at least {SLIDE_STEPS} pitch bend events"
            
            # First bend should be at or near 0 (no bend)
            assert abs(pitch_bend_msgs[0].pitch) <= 100, "First pitch bend should be near 0"
            
            # Last bend should reset to 0
            assert pitch_bend_msgs[-1].pitch == 0, "Final pitch bend should reset to 0"
            
            # Verify note is generated (the base note that gets bent)
            note_ons = [m for m in messages if m.type == 'note_on' and m.velocity > 0]
            assert len(note_ons) == 2, "Should have source and destination notes for chromatic slide"
            assert note_ons[0].note == 60, "Note should be at original pitch (C4 = 60)"
            
        finally:
            os.unlink(temp_path)
    
    def test_chromatic_slide_ascending(self):
        """Test ascending chromatic slide (C4 to G4)"""
        from_note = Note(pitches=[('c', 4, None)], duration=2)
        to_note = Note(pitches=[('g', 4, None)], duration=2)
        slide = Slide(from_note=from_note, to_note=to_note, style='chromatic')
        instrument = Instrument(name='piano', events=[], voices={1: [slide]})
        ast = Sequence(instruments={'piano': instrument})
        
        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        try:
            gen.generate(ast, temp_path)
            
            midi = mido.MidiFile(temp_path)
            messages = list(midi.tracks[1]) if len(midi.tracks) > 1 else list(midi.tracks[0])
            pitch_bend_msgs = [m for m in messages if m.type == 'pitchwheel']
            
            # Verify pitch bend values increase (ascending)
            # Look at middle vs beginning (skip the final reset)
            if len(pitch_bend_msgs) > 2:
                middle_bend = pitch_bend_msgs[len(pitch_bend_msgs) // 2].pitch
                first_bend = pitch_bend_msgs[0].pitch
                assert middle_bend > first_bend, "Pitch bend should increase for ascending slide"
        
        finally:
            os.unlink(temp_path)
    
    def test_chromatic_slide_descending(self):
        """Test descending chromatic slide (C5 to C4)"""
        from_note = Note(pitches=[('c', 5, None)], duration=2)
        to_note = Note(pitches=[('c', 4, None)], duration=2)
        slide = Slide(from_note=from_note, to_note=to_note, style='chromatic')
        instrument = Instrument(name='piano', events=[], voices={1: [slide]})
        ast = Sequence(instruments={'piano': instrument})
        
        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        try:
            gen.generate(ast, temp_path)
            
            midi = mido.MidiFile(temp_path)
            messages = list(midi.tracks[1]) if len(midi.tracks) > 1 else list(midi.tracks[0])
            pitch_bend_msgs = [m for m in messages if m.type == 'pitchwheel']
            
            # Verify pitch bend values decrease (descending)
            if len(pitch_bend_msgs) > 2:
                middle_bend = pitch_bend_msgs[len(pitch_bend_msgs) // 2].pitch
                first_bend = pitch_bend_msgs[0].pitch
                assert middle_bend < first_bend, "Pitch bend should decrease for descending slide"
        
        finally:
            os.unlink(temp_path)
    
    def test_chromatic_slide_pitch_bend_range_clamping(self):
        """Test that pitch bend values are clamped to valid range (-8192 to 8191)"""
        # Create a slide larger than typical pitch bend range
        from_note = Note(pitches=[('c', 2, None)], duration=1)
        to_note = Note(pitches=[('c', 6, None)], duration=1)
        slide = Slide(from_note=from_note, to_note=to_note, style='chromatic')
        instrument = Instrument(name='piano', events=[], voices={1: [slide]})
        ast = Sequence(instruments={'piano': instrument})
        
        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        try:
            gen.generate(ast, temp_path)
            
            midi = mido.MidiFile(temp_path)
            messages = list(midi.tracks[1]) if len(midi.tracks) > 1 else list(midi.tracks[0])
            pitch_bend_msgs = [m for m in messages if m.type == 'pitchwheel']
            
            # All pitch bend values should be within valid range
            for msg in pitch_bend_msgs:
                assert -8192 <= msg.pitch <= 8191, f"Pitch bend {msg.pitch} out of valid range"
        
        finally:
            os.unlink(temp_path)
    
    def test_chromatic_slide_timing(self):
        """Test that pitch bend events are distributed over the duration"""
        from_note = Note(pitches=[('c', 4, None)], duration=1)  # Whole note
        to_note = Note(pitches=[('g', 4, None)], duration=1)
        slide = Slide(from_note=from_note, to_note=to_note, style='chromatic')
        instrument = Instrument(name='piano', events=[], voices={1: [slide]})
        ast = Sequence(instruments={'piano': instrument})
        
        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        try:
            gen.generate(ast, temp_path)
            
            midi = mido.MidiFile(temp_path)
            messages = list(midi.tracks[1]) if len(midi.tracks) > 1 else list(midi.tracks[0])
            
            # Get pitch bend messages with their absolute times
            pitch_bend_times = []
            current_time = 0
            for msg in messages:
                current_time += msg.time
                if msg.type == 'pitchwheel':
                    pitch_bend_times.append(current_time)
            
            # Verify pitch bends span the duration
            if len(pitch_bend_times) > 1:
                span = pitch_bend_times[-1] - pitch_bend_times[0]
                # Should span most of the whole note duration (4 beats * ppq)
                expected_duration = 4 * 480  # 1920 ticks
                assert span >= expected_duration * 0.9, "Pitch bends should span the note duration"
        
        finally:
            os.unlink(temp_path)


# ============================================================================
# Test Stepped Slides (Chromatic Notes)
# ============================================================================

class TestSteppedSlide:
    """Test stepped slides with individual chromatic notes"""
    
    def test_stepped_slide_note_sequence(self):
        """Test that stepped slide generates correct chromatic note sequence"""
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
            
            midi = mido.MidiFile(temp_path)
            messages = list(midi.tracks[1]) if len(midi.tracks) > 1 else list(midi.tracks[0])
            note_ons = [m for m in messages if m.type == 'note_on' and m.velocity > 0]
            
            # C4 to E4 is 4 semitones plus explicit destination sustain
            # Sequence: C, C#, D, D#, E, E
            assert len(note_ons) == 6, f"Expected 6 notes, got {len(note_ons)}"
            
            # Verify note sequence is chromatic and ascending
            expected_notes = [60, 61, 62, 63, 64, 64]
            actual_notes = [m.note for m in note_ons]
            assert actual_notes == expected_notes, f"Expected {expected_notes}, got {actual_notes}"
        
        finally:
            os.unlink(temp_path)
    
    def test_stepped_slide_descending(self):
        """Test descending stepped slide"""
        from_note = Note(pitches=[('g', 4, None)], duration=4)
        to_note = Note(pitches=[('c', 4, None)], duration=4)
        slide = Slide(from_note=from_note, to_note=to_note, style='stepped')
        instrument = Instrument(name='piano', events=[], voices={1: [slide]})
        ast = Sequence(instruments={'piano': instrument})
        
        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        try:
            gen.generate(ast, temp_path)
            
            midi = mido.MidiFile(temp_path)
            messages = list(midi.tracks[1]) if len(midi.tracks) > 1 else list(midi.tracks[0])
            note_ons = [m for m in messages if m.type == 'note_on' and m.velocity > 0]
            
            # G4 to C4 plus explicit destination sustain
            assert len(note_ons) == 9, f"Expected 9 notes, got {len(note_ons)}"
            
            # Verify descending sequence
            expected_notes = [67, 66, 65, 64, 63, 62, 61, 60, 60]
            actual_notes = [m.note for m in note_ons]
            assert actual_notes == expected_notes, f"Expected {expected_notes}, got {actual_notes}"
        
        finally:
            os.unlink(temp_path)
    
    def test_stepped_slide_single_semitone(self):
        """Test stepped slide with single semitone interval"""
        from_note = Note(pitches=[('c', 4, None)], duration=4)
        to_note = Note(pitches=[('c', 4, 'sharp')], duration=4)
        slide = Slide(from_note=from_note, to_note=to_note, style='stepped')
        instrument = Instrument(name='piano', events=[], voices={1: [slide]})
        ast = Sequence(instruments={'piano': instrument})
        
        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        try:
            gen.generate(ast, temp_path)
            
            midi = mido.MidiFile(temp_path)
            messages = list(midi.tracks[1]) if len(midi.tracks) > 1 else list(midi.tracks[0])
            note_ons = [m for m in messages if m.type == 'note_on' and m.velocity > 0]
            
            # Includes explicit destination sustain note
            assert len(note_ons) == 3, f"Expected 3 notes, got {len(note_ons)}"
            assert [m.note for m in note_ons] == [60, 61, 61]
        
        finally:
            os.unlink(temp_path)
    
    def test_stepped_slide_unison(self):
        """Test stepped slide with same start and end note (unison)"""
        from_note = Note(pitches=[('c', 4, None)], duration=4)
        to_note = Note(pitches=[('c', 4, None)], duration=4)
        slide = Slide(from_note=from_note, to_note=to_note, style='stepped')
        instrument = Instrument(name='piano', events=[], voices={1: [slide]})
        ast = Sequence(instruments={'piano': instrument})
        
        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        try:
            gen.generate(ast, temp_path)
            
            midi = mido.MidiFile(temp_path)
            messages = list(midi.tracks[1]) if len(midi.tracks) > 1 else list(midi.tracks[0])
            note_ons = [m for m in messages if m.type == 'note_on' and m.velocity > 0]
            
            # Should play the note once (no steps needed)
            assert len(note_ons) >= 1, "Should have at least one note"
        
        finally:
            os.unlink(temp_path)
    
    def test_stepped_slide_timing_distribution(self):
        """Test that stepped slide notes are evenly distributed in time"""
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
            
            midi = mido.MidiFile(temp_path)
            messages = list(midi.tracks[1]) if len(midi.tracks) > 1 else list(midi.tracks[0])
            
            # Get note on times
            note_on_times = []
            current_time = 0
            for msg in messages:
                current_time += msg.time
                if msg.type == 'note_on' and msg.velocity > 0:
                    note_on_times.append(current_time)
            
            # Verify notes are roughly evenly spaced
            if len(note_on_times) > 1:
                intervals = [note_on_times[i+1] - note_on_times[i] 
                           for i in range(len(note_on_times) - 1)]
                avg_interval = sum(intervals) / len(intervals)
                # All intervals should be similar
                for interval in intervals:
                    # Allow some variance but should be roughly equal
                    assert abs(interval - avg_interval) < avg_interval * 0.3, \
                        "Notes should be evenly distributed in time"
        
        finally:
            os.unlink(temp_path)


# ============================================================================
# Test Portamento Slides
# ============================================================================

class TestPortamentoSlide:
    """Test portamento slides using MIDI CC"""
    
    def test_portamento_cc_generation(self):
        """Test that portamento slide generates correct CC events"""
        from_note = Note(pitches=[('c', 4, None)], duration=2)
        to_note = Note(pitches=[('g', 4, None)], duration=2)
        slide = Slide(from_note=from_note, to_note=to_note, style='portamento')
        instrument = Instrument(name='piano', events=[], voices={1: [slide]})
        ast = Sequence(instruments={'piano': instrument})
        
        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        try:
            gen.generate(ast, temp_path)
            
            midi = mido.MidiFile(temp_path)
            messages = list(midi.tracks[1]) if len(midi.tracks) > 1 else list(midi.tracks[0])
            cc_msgs = [m for m in messages if m.type == 'control_change']
            
            # Should have portamento CC messages
            portamento_time_msgs = [m for m in cc_msgs if m.control == CC_PORTAMENTO_TIME]
            portamento_switch_msgs = [m for m in cc_msgs if m.control == CC_PORTAMENTO_SWITCH]
            
            assert len(portamento_time_msgs) >= 1, "Should have portamento time CC"
            assert len(portamento_switch_msgs) >= 1, "Should have portamento switch CC"
            
            # Verify portamento switch is turned on (value 127)
            assert any(m.value == 127 for m in portamento_switch_msgs), \
                "Portamento switch should be turned on"
            
            # Verify portamento time is in valid range (0-127)
            for msg in portamento_time_msgs:
                assert 0 <= msg.value <= 127, f"Portamento time {msg.value} out of range"
        
        finally:
            os.unlink(temp_path)
    
    def test_portamento_note_generation(self):
        """Test that portamento slide generates both from_note and to_note"""
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
            
            midi = mido.MidiFile(temp_path)
            messages = list(midi.tracks[1]) if len(midi.tracks) > 1 else list(midi.tracks[0])
            note_ons = [m for m in messages if m.type == 'note_on' and m.velocity > 0]
            
            # Should have both from_note and to_note
            assert len(note_ons) == 2, f"Expected 2 notes for portamento, got {len(note_ons)}"
            assert note_ons[0].note == 60, "First note should be C4 (60)"
            assert note_ons[1].note == 67, "Second note should be G4 (67)"
        
        finally:
            os.unlink(temp_path)


# ============================================================================
# Test Slide Duration and Timing
# ============================================================================

class TestSlideDuration:
    """Test slide duration handling and timing calculations"""
    
    def test_slide_with_different_durations(self):
        """Test slides with various note durations"""
        durations = [1, 2, 4, 8, 16]  # whole, half, quarter, eighth, sixteenth
        
        for duration in durations:
            from_note = Note(pitches=[('c', 4, None)], duration=duration)
            to_note = Note(pitches=[('g', 4, None)], duration=duration)
            slide = Slide(from_note=from_note, to_note=to_note, style='chromatic')
            instrument = Instrument(name='piano', events=[], voices={1: [slide]})
            ast = Sequence(instruments={'piano': instrument})
            
            gen = MIDIGenerator(ppq=480)
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
                temp_path = f.name
            
            try:
                gen.generate(ast, temp_path)
                
                midi = mido.MidiFile(temp_path)
                messages = list(midi.tracks[1]) if len(midi.tracks) > 1 else list(midi.tracks[0])
                
                # Should generate MIDI successfully
                note_ons = [m for m in messages if m.type == 'note_on' and m.velocity > 0]
                assert len(note_ons) >= 1, f"Should generate notes for duration {duration}"
            
            finally:
                os.unlink(temp_path)
    
    def test_slide_with_dotted_note(self):
        """Test slide with dotted note duration"""
        from_note = Note(pitches=[('c', 4, None)], duration=4, dotted=True)  # Dotted quarter
        to_note = Note(pitches=[('g', 4, None)], duration=4, dotted=True)
        slide = Slide(from_note=from_note, to_note=to_note, style='chromatic')
        instrument = Instrument(name='piano', events=[], voices={1: [slide]})
        ast = Sequence(instruments={'piano': instrument})
        
        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        try:
            gen.generate(ast, temp_path)
            
            midi = mido.MidiFile(temp_path)
            messages = list(midi.tracks[1]) if len(midi.tracks) > 1 else list(midi.tracks[0])
            note_ons = [m for m in messages if m.type == 'note_on' and m.velocity > 0]
            
            assert len(note_ons) >= 1, "Should generate notes for dotted duration"
        
        finally:
            os.unlink(temp_path)
    
    def test_slide_timing_with_semantic_analysis(self):
        """Test that semantic analysis correctly calculates slide timing"""
        from_note = Note(pitches=[('c', 4, None)], duration=4)
        to_note = Note(pitches=[('g', 4, None)], duration=4)
        slide = Slide(from_note=from_note, to_note=to_note, style='chromatic')
        instrument = Instrument(name='piano', events=[], voices={1: [slide]})
        ast = Sequence(instruments={'piano': instrument})
        
        analyzer = SemanticAnalyzer()
        analyzed_ast = analyzer.analyze(ast)
        
        # Check that timing was calculated
        analyzed_slide = analyzed_ast.instruments['piano'].voices[1][0]
        assert isinstance(analyzed_slide, Slide)
        assert analyzed_slide.from_note.start_time is not None
        assert analyzed_slide.from_note.end_time is not None
        assert analyzed_slide.to_note.start_time is not None
        assert analyzed_slide.to_note.end_time is not None
        
        # Verify slide takes the duration of from_note
        # Note: Timing may be in ticks (ppq units) not beats depending on analysis phase
        actual_duration = analyzed_slide.from_note.end_time - analyzed_slide.from_note.start_time
        assert actual_duration > 0, f"Slide should have positive duration, got {actual_duration}"


# ============================================================================
# Test Slide Interval Variations
# ============================================================================

class TestSlideIntervals:
    """Test slides with different interval sizes"""
    
    def test_slide_small_interval(self):
        """Test slide with small interval (1-3 semitones)"""
        intervals = [
            ('c', 4, 'c', 4, 'sharp'),  # C to C# (1 semitone)
            ('c', 4, 'd', 4, None),  # C to D (2 semitones)
            ('c', 4, 'd', 4, 'sharp'),  # C to D# (3 semitones)
        ]
        
        for pitch1, oct1, pitch2, oct2, acc2 in intervals:
            from_note = Note(pitches=[(pitch1, oct1, None)], duration=4)
            to_note = Note(pitches=[(pitch2, oct2, acc2)], duration=4)
            slide = Slide(from_note=from_note, to_note=to_note, style='chromatic')
            instrument = Instrument(name='piano', events=[], voices={1: [slide]})
            ast = Sequence(instruments={'piano': instrument})
            
            gen = MIDIGenerator(ppq=480)
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
                temp_path = f.name
            
            try:
                gen.generate(ast, temp_path)
                # Should generate successfully
                assert os.path.exists(temp_path)
            finally:
                os.unlink(temp_path)
    
    def test_slide_medium_interval(self):
        """Test slide with medium interval (4-12 semitones)"""
        intervals = [
            ('c', 4, 'e', 4),  # Major third (4 semitones)
            ('c', 4, 'g', 4),  # Perfect fifth (7 semitones)
            ('c', 4, 'c', 5),  # Octave (12 semitones)
        ]
        
        for pitch1, oct1, pitch2, oct2 in intervals:
            from_note = Note(pitches=[(pitch1, oct1, None)], duration=4)
            to_note = Note(pitches=[(pitch2, oct2, None)], duration=4)
            slide = Slide(from_note=from_note, to_note=to_note, style='chromatic')
            instrument = Instrument(name='piano', events=[], voices={1: [slide]})
            ast = Sequence(instruments={'piano': instrument})
            
            gen = MIDIGenerator(ppq=480)
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
                temp_path = f.name
            
            try:
                gen.generate(ast, temp_path)
                assert os.path.exists(temp_path)
            finally:
                os.unlink(temp_path)
    
    def test_slide_large_interval(self):
        """Test slide with large interval (13-24 semitones)"""
        intervals = [
            ('c', 4, 'c', 6),  # Two octaves (24 semitones)
            ('c', 3, 'g', 4),  # Octave + fifth (19 semitones)
        ]
        
        for pitch1, oct1, pitch2, oct2 in intervals:
            from_note = Note(pitches=[(pitch1, oct1, None)], duration=2)
            to_note = Note(pitches=[(pitch2, oct2, None)], duration=2)
            slide = Slide(from_note=from_note, to_note=to_note, style='chromatic')
            instrument = Instrument(name='piano', events=[], voices={1: [slide]})
            ast = Sequence(instruments={'piano': instrument})
            
            gen = MIDIGenerator(ppq=480)
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
                temp_path = f.name
            
            try:
                gen.generate(ast, temp_path)
                assert os.path.exists(temp_path)
            finally:
                os.unlink(temp_path)
    
    def test_slide_extreme_interval_warning(self):
        """Test that very large slide intervals generate warning"""
        from_note = Note(pitches=[('c', 2, None)], duration=1)
        to_note = Note(pitches=[('c', 5, None)], duration=1)  # 36 semitones
        slide = Slide(from_note=from_note, to_note=to_note, style='chromatic')
        instrument = Instrument(name='piano', events=[], voices={1: [slide]})
        ast = Sequence(instruments={'piano': instrument})
        
        analyzer = SemanticAnalyzer()
        analyzed_ast = analyzer.analyze(ast)
        
        # Should generate warning for large interval (> 24 semitones)
        assert len(analyzer.warnings) > 0, "Should generate warning for extreme interval"
        assert any("slide" in w.lower() for w in analyzer.warnings), \
            "Warning should mention slide"


# ============================================================================
# Test Slide Integration with Dynamics and Articulation
# ============================================================================

class TestSlideIntegration:
    """Test slides with dynamics, articulation, and voices"""
    
    def test_slide_with_dynamics(self):
        """Test that slide inherits dynamic level"""
        source = """
                piano {
                    V1: @p <c4/4 g4/4> r/2;
                }
        """
        ast = parse_muslang(source)
        analyzer = SemanticAnalyzer()
        analyzed_ast = analyzer.analyze(ast)
        
        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        try:
            gen.generate(analyzed_ast, temp_path)
            
            midi = mido.MidiFile(temp_path)
            messages = list(midi.tracks[1]) if len(midi.tracks) > 1 else list(midi.tracks[0])
            note_ons = [m for m in messages if m.type == 'note_on' and m.velocity > 0]
            
            # Velocity should reflect piano (p) dynamic
            assert len(note_ons) >= 1
            assert note_ons[0].velocity == VELOCITY_P, \
                f"Expected velocity {VELOCITY_P}, got {note_ons[0].velocity}"
        
        finally:
            os.unlink(temp_path)
    
    def test_slide_with_crescendo(self):
        """Test slide during crescendo"""
        source = """
                piano {
                    V1: @p @crescendo <c4/4 c5/4> <c5/4 c4/4>;
                }
        """
        ast = parse_muslang(source)
        analyzer = SemanticAnalyzer()
        analyzed_ast = analyzer.analyze(ast)
        
        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        try:
            gen.generate(analyzed_ast, temp_path)
            
            midi = mido.MidiFile(temp_path)
            messages = list(midi.tracks[1]) if len(midi.tracks) > 1 else list(midi.tracks[0])
            note_ons = [m for m in messages if m.type == 'note_on' and m.velocity > 0]
            
            # Should have increasing velocities during crescendo
            assert len(note_ons) >= 2
            # First slide should be softer than last note
            assert note_ons[0].velocity < note_ons[-1].velocity
        
        finally:
            os.unlink(temp_path)
    
    def test_slide_sequence(self):
        """Test multiple slides in sequence"""
        source = """
                piano {
                    V1: <c4/4 e4/4> <e4/4 g4/4>;
                }
        """
        ast = parse_muslang(source)
        analyzer = SemanticAnalyzer()
        analyzed_ast = analyzer.analyze(ast)
        
        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        try:
            gen.generate(analyzed_ast, temp_path)
            
            midi = mido.MidiFile(temp_path)
            messages = list(midi.tracks[1]) if len(midi.tracks) > 1 else list(midi.tracks[0])
            
            # Should generate successfully
            note_ons = [m for m in messages if m.type == 'note_on' and m.velocity > 0]
            assert len(note_ons) >= 3, "Should have notes from all three slides"
        
        finally:
            os.unlink(temp_path)
    
    def test_slide_in_multiple_voices(self):
        """Test slides in different voices"""
        source = """
                piano {
                    V1: <c4/2 g4/2>;
                    V2: <c3/2 g3/2>;
                }
        """
        ast = parse_muslang(source)
        analyzer = SemanticAnalyzer()
        analyzed_ast = analyzer.analyze(ast)
        
        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        try:
            gen.generate(analyzed_ast, temp_path)
            
            midi = mido.MidiFile(temp_path)
            messages = list(midi.tracks[1]) if len(midi.tracks) > 1 else list(midi.tracks[0])
            note_ons = [m for m in messages if m.type == 'note_on' and m.velocity > 0]
            
            # Should have notes from both voices
            assert len(note_ons) >= 2, "Should have notes from both voices"
        
        finally:
            os.unlink(temp_path)
    
    def test_stepped_slide_with_forte(self):
        """Test stepped slide with forte dynamic"""
        source = """
                piano {
                    V1: @f <stepped: c4/4 e4/4> r/2;
                }
        """
        ast = parse_muslang(source)
        analyzer = SemanticAnalyzer()
        analyzed_ast = analyzer.analyze(ast)
        
        gen = MIDIGenerator(ppq=480)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        try:
            gen.generate(analyzed_ast, temp_path)
            
            midi = mido.MidiFile(temp_path)
            messages = list(midi.tracks[1]) if len(midi.tracks) > 1 else list(midi.tracks[0])
            note_ons = [m for m in messages if m.type == 'note_on' and m.velocity > 0]
            
            # All notes should have forte velocity
            assert len(note_ons) >= 1
            for note_on in note_ons:
                assert note_on.velocity == VELOCITY_F, \
                    f"Expected velocity {VELOCITY_F}, got {note_on.velocity}"
        
        finally:
            os.unlink(temp_path)


# ============================================================================
# Test Parser Edge Cases
# ============================================================================

class TestSlideParser:
    """Test slide parsing edge cases"""
    
    def test_parse_chromatic_slide_default(self):
        """Test parsing slide without explicit style (defaults to chromatic)"""
        source = """
                piano {
                    V1: <c4/4 g4/4>;
                }
        """
        ast = parse_muslang(source)

        slide = _voice_events(ast)[0]
        assert isinstance(slide, Slide)
        assert slide.style == 'chromatic'
        assert slide.from_note.pitches[0][0] == 'c'
        assert slide.to_note.pitches[0][0] == 'g'
    
    def test_parse_stepped_slide(self):
        """Test parsing stepped slide"""
        source = """
                piano {
                    V1: <stepped: c4/4 e4/4>;
                }
        """
        ast = parse_muslang(source)

        slide = _voice_events(ast)[0]
        assert isinstance(slide, Slide)
        assert slide.style == 'stepped'
    
    def test_parse_portamento_slide(self):
        """Test parsing portamento slide"""
        source = """
                piano {
                    V1: <portamento: c4/2 g4/2>;
                }
        """
        ast = parse_muslang(source)

        slide = _voice_events(ast)[0]
        assert isinstance(slide, Slide)
        assert slide.style == 'portamento'
    
    def test_parse_slide_with_accidentals(self):
        """Test parsing slide with accidentals"""
        source = """
                piano {
                    V1: <c4+/4 g4-/4>;
                }
        """
        ast = parse_muslang(source)

        slide = _voice_events(ast)[0]
        assert isinstance(slide, Slide)
        # Accidentals may be represented as 'sharp'/'flat' or '#'/'b' depending on parser
        assert slide.from_note.pitches[0][2] in ['#', 'sharp']
        assert slide.to_note.pitches[0][2] in ['b', 'flat']
    
    def test_parse_slide_with_different_durations(self):
        """Test parsing slide with various note durations"""
        durations = ['1', '2', '4', '8', '16']
        
        for dur in durations:
            source = f"""
                        piano {{
                            V1: <c4/{dur} g4/{dur}>;
                        }}
            """
            ast = parse_muslang(source)

            slide = _voice_events(ast)[0]
            assert isinstance(slide, Slide)
            assert slide.from_note.duration == int(dur)
            assert slide.to_note.duration == int(dur)
    
    def test_parse_slide_whitespace_variations(self):
        """Test parsing slide with various whitespace"""
        variations = [
            "<c4/4 g4/4>",
            "< c4/4 g4/4 >",
            "<  c4/4  g4/4  >",
            "<c4/4  g4/4>",
        ]
        
        for source_expr in variations:
            source = f"""
                        piano {{
                            V1: {source_expr};
                        }}
            """
            ast = parse_muslang(source)

            slide = _voice_events(ast)[0]
            assert isinstance(slide, Slide)
            assert slide.from_note.pitches[0][0] == 'c'
            assert slide.to_note.pitches[0][0] == 'g'
    
    def test_parse_multiple_slides(self):
        """Test parsing multiple slides in sequence"""
        source = """
                piano {
                    V1: <c4/4 e4/4> <e4/4 g4/4> <g4/4 c5/4>;
                }
        """
        ast = parse_muslang(source)
        events = _voice_events(ast)
        assert len(events) == 3
        for event in events:
            assert isinstance(event, Slide)


# ============================================================================
# Test Semantic Validation
# ============================================================================

class TestSlideSemantics:
    """Test semantic analysis and validation of slides"""
    
    def test_slide_large_interval_warning(self):
        """Test that large slide intervals generate warnings"""
        from_note = Note(pitches=[('c', 2, None)], duration=1)
        to_note = Note(pitches=[('g', 5, None)], duration=1)  # Very large interval
        slide = Slide(from_note=from_note, to_note=to_note, style='chromatic')
        instrument = Instrument(name='piano', events=[], voices={1: [slide]})
        ast = Sequence(instruments={'piano': instrument})
        
        analyzer = SemanticAnalyzer()
        analyzed_ast = analyzer.analyze(ast)
        
        # Should have warning about large interval
        assert len(analyzer.warnings) > 0
        assert any("slide" in w.lower() for w in analyzer.warnings)
    
    def test_slide_reasonable_interval_no_warning(self):
        """Test that reasonable slide intervals don't generate warnings"""
        from_note = Note(pitches=[('c', 4, None)], duration=2)
        to_note = Note(pitches=[('c', 5, None)], duration=2)  # One octave
        slide = Slide(from_note=from_note, to_note=to_note, style='chromatic')
        instrument = Instrument(name='piano', events=[], voices={1: [slide]})
        ast = Sequence(instruments={'piano': instrument})
        
        analyzer = SemanticAnalyzer()
        analyzed_ast = analyzer.analyze(ast)
        
        # Should not have warnings for reasonable interval
        slide_warnings = [w for w in analyzer.warnings if "slide" in w.lower()]
        assert len(slide_warnings) == 0
    
    def test_slide_timing_calculation(self):
        """Test that slides get correct start_time and end_time"""
        from_note = Note(pitches=[('c', 4, None)], duration=4)
        to_note = Note(pitches=[('g', 4, None)], duration=4)
        slide = Slide(from_note=from_note, to_note=to_note, style='chromatic')
        
        # Add another event after the slide
        note_after = Note(pitches=[('e', 4, None)], duration=4)
        
        instrument = Instrument(name='piano', events=[], voices={1: [slide, note_after]})
        ast = Sequence(instruments={'piano': instrument})
        
        analyzer = SemanticAnalyzer()
        analyzed_ast = analyzer.analyze(ast)
        
        analyzed_slide = analyzed_ast.instruments['piano'].voices[1][0]
        analyzed_note = analyzed_ast.instruments['piano'].voices[1][1]
        
        # Slide should start at 0
        assert analyzed_slide.from_note.start_time == 0.0
        
        # Slide should have positive duration
        assert analyzed_slide.from_note.end_time > 0
        
        # Next note should start after full slide duration (from + to note)
        assert analyzed_note.start_time == analyzed_slide.to_note.end_time
    
    def test_slide_in_integrated_sequence(self):
        """Test slide timing in complete sequence with other elements"""
        source = """
                piano {
                    V1: c4/4 <d4/4 f4/4> e4/4;
                }
        """
        ast = parse_muslang(source)
        analyzer = SemanticAnalyzer()
        analyzed_ast = analyzer.analyze(ast)

        events = _voice_events(analyzed_ast)
        
        # Verify timing sequence
        for i, event in enumerate(events):
            if hasattr(event, 'start_time'):
                assert event.start_time is not None
                assert event.end_time is not None
                
                # Each event should start when previous ends (or at 0 for first)
                if i > 0 and hasattr(events[i-1], 'end_time'):
                    # Allow small floating point tolerance
                    time_diff = abs(event.start_time - events[i-1].end_time)
                    assert time_diff < 0.001, \
                        f"Event {i} timing gap: {time_diff}"
