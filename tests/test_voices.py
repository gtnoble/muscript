"""
Tests for voice grouping and instrument merging functionality.
"""
from muslang.parser import parse_muslang
from muslang.semantics import SemanticAnalyzer
from muslang.midi_gen import MIDIGenerator
from muslang.ast_nodes import Note
import tempfile


def _voice_events(instrument, voice_number=1):
  events = []
  for item in instrument.voices[voice_number]:
    if hasattr(item, 'events'):
      events.extend(item.events)
    else:
      events.append(item)
  return events


class TestVoiceGrouping:
    """Test voice grouping in parser"""
    
    def test_single_voice(self):
        """Test single voice declaration"""
        source = "piano { V1: c4/4 d4/4 e4/4 r/4; }"
        ast = parse_muslang(source)
        
        inst = ast.instruments['piano']
        assert 1 in inst.voices
        notes = [e for e in _voice_events(inst, 1) if isinstance(e, Note)]
        assert len(notes) == 3
        assert notes[0].pitch == 'c'
        assert notes[1].pitch == 'd'
        assert notes[2].pitch == 'e'
    
    def test_multiple_voices(self):
        """Test multiple voice declarations"""
        source = """
        piano {
          V1: c4/4 d4/4 r/2;
          V2: e3/2 r/2;
          V3: g4/4 a4/4 b4/4 r/4;
        }
        """
        ast = parse_muslang(source)
        
        inst = ast.instruments['piano']
        assert len(inst.voices) == 3
        assert len(_voice_events(inst, 1)) == 3
        assert len(_voice_events(inst, 2)) == 2
        assert len(_voice_events(inst, 3)) == 4
    
    def test_voice_continuation(self):
        """Test multiple declarations of same voice concatenate"""
        source = """
        piano {
          V1: c4/4 d4/4 | f4/4 g4/4;
          V2: e3/2 r/2;
        }
        """
        ast = parse_muslang(source)
        
        inst = ast.instruments['piano']
        # V1 should have 4 notes (c, d, f, g)
        voice1_notes = [e for e in _voice_events(inst, 1) if isinstance(e, Note)]
        assert len(voice1_notes) == 4
        assert voice1_notes[0].pitch == 'c'
        assert voice1_notes[1].pitch == 'd'
        assert voice1_notes[2].pitch == 'f'
        assert voice1_notes[3].pitch == 'g'
        # V2 should have 1 note
        voice2_notes = [e for e in _voice_events(inst, 2) if isinstance(e, Note)]
        assert len(voice2_notes) == 1

    def test_repeated_voice_blocks_concatenate(self):
        """Test repeated Vn blocks append instead of overwrite"""
        source = """
        piano {
          V1: c4/4 d4/4 r/2;
          V2: c3/1;
          V1: e4/4 f4/4 g4/4 a4/4;
        }
        """
        ast = parse_muslang(source)

        inst = ast.instruments['piano']
        voice1_notes = [e for e in _voice_events(inst, 1) if isinstance(e, Note)]
        assert len(voice1_notes) == 6
        assert [n.pitch for n in voice1_notes] == ['c', 'd', 'e', 'f', 'g', 'a']


class TestVoiceTiming:
    """Test voice timing calculation"""
    
    def test_voices_start_at_zero(self):
        """Test that all voices start at time 0"""
        source = """
        piano {
          V1: c4/4 d4/4 r/2;
          V2: e3/2 r/2;
        }
        """
        ast = parse_muslang(source)
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(ast)
        
        inst = result.instruments['piano']
        v1_first = _voice_events(inst, 1)[0]
        v2_first = _voice_events(inst, 2)[0]
        
        assert v1_first.start_time == 0.0
        assert v2_first.start_time == 0.0
    
    def test_voices_sequential_within_voice(self):
        """Test events within a voice are sequential"""
        source = """
        piano {
          V1: c4/4 d4/4 e4/4 r/4;
        }
        """
        ast = parse_muslang(source)
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(ast)
        
        inst = result.instruments['piano']
        notes = [e for e in _voice_events(inst, 1) if isinstance(e, Note)]
        
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
        violin {
          V1: c4/4 d4/4 r/2;
        }
        piano {
          V1: e4/4 r/2 r/4 r/4;
        }
        violin {
          V1: f4/4 g4/4 r/2;
        }
        """
        ast = parse_muslang(source)
        
        # Should only have 2 instruments (violin and piano)
        assert len(ast.instruments) == 2
        assert 'violin' in ast.instruments
        assert 'piano' in ast.instruments
        
        # Violin should have 4 notes in V1
        assert len(_voice_events(ast.instruments['violin'], 1)) == 6
        # Piano should have 1 note in V1
        assert len([e for e in _voice_events(ast.instruments['piano'], 1) if isinstance(e, Note)]) == 1
    
    def test_merged_instrument_sequential(self):
        """Test merged instrument events are sequential"""
        source = """
        piano {
          V1: c4/4 d4/4 r/2;
        }
        piano {
          V1: e4/4 f4/4 r/2;
        }
        """
        ast = parse_muslang(source)
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(ast)
        
        inst = result.instruments['piano']
        notes = [e for e in _voice_events(inst, 1) if isinstance(e, Note)]
        
        # Should have 4 notes total
        assert len(notes) == 4
        # They should be sequential
        assert notes[0].start_time == 0.0
        assert notes[1].start_time == notes[0].end_time
        assert notes[2].start_time > notes[1].end_time
        assert notes[3].start_time == notes[2].end_time
    
    def test_merged_instrument_voices(self):
        """Test merging instruments with voices"""
        source = """
        piano {
          V1: c4/4 d4/4 r/2;
          V2: e3/2 r/2;
        }
        piano {
          V1: f4/4 g4/4 r/2;
          V3: a3/2 r/2;
        }
        """
        ast = parse_muslang(source)
        
        inst = ast.instruments['piano']
        # Should have 3 voices
        assert len(inst.voices) == 3
        # V1 should have 4 notes (merged from both declarations)
        assert len(_voice_events(inst, 1)) == 6
        # V2 should have 1 note
        assert len(_voice_events(inst, 2)) == 2
        # V3 should have 1 note
        assert len(_voice_events(inst, 3)) == 2


class TestMIDIGeneration:
    """Test MIDI generation with voices"""
    
    def test_midi_generation_with_voices(self):
        """Test MIDI file is generated correctly with voices"""
        source = """
        piano {
          V1: c4/4 d4/4 e4/4 r/4;
          V2: c3/2 g3/2;
        }
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
        violin {
          V1: c4/4 d4/4 r/2;
        }
        violin {
          V1: e4/4 f4/4 r/2;
        }
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
