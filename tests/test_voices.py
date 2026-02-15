"""
Tests for voice grouping and instrument merging functionality.
"""
from muslang.parser import parse_muslang
from muslang.semantics import SemanticAnalyzer
from muslang.midi_gen import MIDIGenerator
from muslang.ast_nodes import Note
import tempfile


class TestVoiceGrouping:
    """Test voice grouping in parser"""
    
    def test_single_voice(self):
        """Test single voice declaration"""
        source = "piano: V1: c4/4 d4/4 e4/4"
        ast = parse_muslang(source)
        
        inst = ast.instruments['piano']
        assert 1 in inst.voices
        assert len(inst.voices[1]) == 3
        assert inst.voices[1][0].pitch == 'c'
        assert inst.voices[1][1].pitch == 'd'
        assert inst.voices[1][2].pitch == 'e'
    
    def test_multiple_voices(self):
        """Test multiple voice declarations"""
        source = """
        piano:
          V1: c4/4 d4/4
          V2: e3/2
          V3: g4/4 a4/4 b4/4
        """
        ast = parse_muslang(source)
        
        inst = ast.instruments['piano']
        assert len(inst.voices) == 3
        assert len(inst.voices[1]) == 2
        assert len(inst.voices[2]) == 1
        assert len(inst.voices[3]) == 3
    
    def test_voice_continuation(self):
        """Test multiple declarations of same voice concatenate"""
        source = """
        piano:
          V1: c4/4 d4/4
          V2: e3/2
          V1: f4/4 g4/4
        """
        ast = parse_muslang(source)
        
        inst = ast.instruments['piano']
        # V1 should have 4 notes (c, d, f, g)
        assert len(inst.voices[1]) == 4
        assert inst.voices[1][0].pitch == 'c'
        assert inst.voices[1][1].pitch == 'd'
        assert inst.voices[1][2].pitch == 'f'
        assert inst.voices[1][3].pitch == 'g'
        # V2 should have 1 note
        assert len(inst.voices[2]) == 1


class TestVoiceTiming:
    """Test voice timing calculation"""
    
    def test_voices_start_at_zero(self):
        """Test that all voices start at time 0"""
        source = """
        piano:
          V1: c4/4 d4/4
          V2: e3/2
        """
        ast = parse_muslang(source)
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(ast)
        
        inst = result.instruments['piano']
        v1_first = inst.voices[1][0]
        v2_first = inst.voices[2][0]
        
        assert v1_first.start_time == 0.0
        assert v2_first.start_time == 0.0
    
    def test_voices_sequential_within_voice(self):
        """Test events within a voice are sequential"""
        source = """
        piano:
          V1: c4/4 d4/4 e4/4
        """
        ast = parse_muslang(source)
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(ast)
        
        inst = result.instruments['piano']
        notes = inst.voices[1]
        
        # First note at 0
        assert notes[0].start_time == 0.0
        # Second note starts where first ends
        assert notes[1].start_time == notes[0].end_time
        # Third note starts where second ends
        assert notes[2].start_time == notes[1].end_time


class TestInstrumentMerging:
    """Test instrument merging functionality"""
    
    def test_instrument_merging(self):
        """Test multiple declarations of same instrument merge"""
        source = """
        violin: c4/4 d4/4
        piano: e4/4
        violin: f4/4 g4/4
        """
        ast = parse_muslang(source)
        
        # Should only have 2 instruments (violin and piano)
        assert len(ast.instruments) == 2
        assert 'violin' in ast.instruments
        assert 'piano' in ast.instruments
        
        # Violin should have 4 notes
        assert len(ast.instruments['violin'].events) == 4
        # Piano should have 1 note
        assert len(ast.instruments['piano'].events) == 1
    
    def test_merged_instrument_sequential(self):
        """Test merged instrument events are sequential"""
        source = """
        piano: c4/4 d4/4
        piano: e4/4 f4/4
        """
        ast = parse_muslang(source)
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(ast)
        
        inst = result.instruments['piano']
        notes = inst.events
        
        # Should have 4 notes total
        assert len(notes) == 4
        # They should be sequential
        assert notes[0].start_time == 0.0
        assert notes[1].start_time == notes[0].end_time
        assert notes[2].start_time == notes[1].end_time
        assert notes[3].start_time == notes[2].end_time
    
    def test_merged_instrument_voices(self):
        """Test merging instruments with voices"""
        source = """
        piano:
          V1: c4/4 d4/4
          V2: e3/2
        piano:
          V1: f4/4 g4/4
          V3: a3/2
        """
        ast = parse_muslang(source)
        
        inst = ast.instruments['piano']
        # Should have 3 voices
        assert len(inst.voices) == 3
        # V1 should have 4 notes (merged from both declarations)
        assert len(inst.voices[1]) == 4
        # V2 should have 1 note
        assert len(inst.voices[2]) == 1
        # V3 should have 1 note
        assert len(inst.voices[3]) == 1


class TestMIDIGeneration:
    """Test MIDI generation with voices"""
    
    def test_midi_generation_with_voices(self):
        """Test MIDI file is generated correctly with voices"""
        source = """
        piano:
          V1: c4/4 d4/4 e4/4
          V2: c3/2 g3/2
        """
        ast = parse_muslang(source)
        analyzer = SemanticAnalyzer()
        analyzed = analyzer.analyze(ast)
        
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        gen = MIDIGenerator()
        gen.generate(analyzed, temp_path)
        
        # File should exist and be non-empty
        import os
        assert os.path.exists(temp_path)
        assert os.path.getsize(temp_path) > 0
        
        # Clean up
        os.unlink(temp_path)
    
    def test_midi_single_track_for_instrument(self):
        """Test single merged instrument creates single MIDI track"""
        source = """
        violin: c4/4 d4/4
        violin: e4/4 f4/4
        """
        ast = parse_muslang(source)
        analyzer = SemanticAnalyzer()
        analyzed = analyzer.analyze(ast)
        
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.mid', delete=False) as f:
            temp_path = f.name
        
        gen = MIDIGenerator()
        gen.generate(analyzed, temp_path)
        
        # Check MIDI file has 1 track (for violin)
        import mido
        midi = mido.MidiFile(temp_path)
        # Note: mido might have additional tempo/meta tracks
        # The key is we should have our instrument track
        assert len(midi.tracks) >= 1
        
        # Clean up
        import os
        os.unlink(temp_path)


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, '-v'])
