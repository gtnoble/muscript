"""
Tests for stack-based reset system with :reset and @reset.

Tests that articulation and dynamic changes push to their respective stacks,
and that :reset/:@reset pop from the appropriate stack.
"""

import pytest
from muslang.ast_nodes import (
    Sequence, Instrument, Voice, Note, Rest, Measure,
    Articulation, DynamicLevel, DynamicTransition, Reset
)
from muslang.semantics import SemanticAnalyzer


class TestBasicStackOperations:
    """Test basic push/pop operations on articulation and dynamic stacks."""
    
    def test_articulation_push_and_pop(self):
        """Test that articulation changes push to stack and :reset pops."""
        events = [
            Articulation(type='staccato'),
            Note(pitches=[('c', 4, None)], duration=4),
            Articulation(type='legato'),
            Note(pitches=[('d', 4, None)], duration=4),
            Reset(type='articulation'),  # Should pop legato, back to staccato
            Note(pitches=[('e', 4, None)], duration=4),
        ]
        instrument = Instrument(name='piano', events=[], voices={1: events})
        seq = Sequence(events=[instrument])
        
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(seq)
        
        processed_events = result.events[0].voices[1]
        
        # First note: staccato (first articulation)
        assert processed_events[1].articulation == 'staccato'
        
        # Second note: legato (second articulation)
        assert processed_events[3].articulation == 'legato'
        
        # Third note: staccato (after reset, popped back to staccato)
        assert processed_events[5].articulation == 'staccato'
    
    def test_dynamic_push_and_pop(self):
        """Test that dynamic changes push to stack and @reset pops."""
        events = [
            DynamicLevel(level='p'),
            Note(pitches=[('c', 4, None)], duration=4),
            DynamicLevel(level='f'),
            Note(pitches=[('d', 4, None)], duration=4),
            Reset(type='dynamic'),  # Should pop f, back to p
            Note(pitches=[('e', 4, None)], duration=4),
        ]
        instrument = Instrument(name='piano', events=[], voices={1: events})
        seq = Sequence(events=[instrument])
        
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(seq)
        
        processed_events = result.events[0].voices[1]
        
        # First note: p (piano)
        assert processed_events[1].dynamic_level == 'p'
        
        # Second note: f (forte)
        assert processed_events[3].dynamic_level == 'f'
        
        # Third note: p (after reset, popped back to p)
        assert processed_events[5].dynamic_level == 'p'
    
    def test_multiple_pushes_and_pops(self):
        """Test multiple articulation changes followed by multiple resets."""
        events = [
            Articulation(type='staccato'),
            Articulation(type='legato'),
            Articulation(type='tenuto'),
            Note(pitches=[('c', 4, None)], duration=4),  # tenuto
            Reset(type='articulation'),
            Note(pitches=[('d', 4, None)], duration=4),  # legato
            Reset(type='articulation'),
            Note(pitches=[('e', 4, None)], duration=4),  # staccato
            Reset(type='articulation'),
            Note(pitches=[('f', 4, None)], duration=4),  # natural (system default)
        ]
        instrument = Instrument(name='piano', events=[], voices={1: events})
        seq = Sequence(events=[instrument])
        
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(seq)
        
        processed_events = result.events[0].voices[1]
        
        # After 3 pushes: tenuto
        assert processed_events[3].articulation == 'tenuto'
        
        # After 1 pop: legato
        assert processed_events[5].articulation == 'legato'
        
        # After 2 pops: staccato
        assert processed_events[7].articulation == 'staccato'
        
        # After 3 pops: natural (system default at bottom of stack)
        assert processed_events[9].articulation == 'natural'


class TestStackIndependence:
    """Test that articulation and dynamic stacks are independent."""
    
    def test_articulation_reset_doesnt_affect_dynamics(self):
        """Test that :reset only affects articulation, not dynamics."""
        events = [
            DynamicLevel(level='f'),
            Articulation(type='staccato'),
            Note(pitches=[('c', 4, None)], duration=4),
            Reset(type='articulation'),  # Only pops articulation
            Note(pitches=[('d', 4, None)], duration=4),
        ]
        instrument = Instrument(name='piano', events=[], voices={1: events})
        seq = Sequence(events=[instrument])
        
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(seq)
        
        processed_events = result.events[0].voices[1]
        
        # Second note should have natural articulation but still f dynamic
        assert processed_events[4].articulation == 'natural'
        assert processed_events[4].dynamic_level == 'f'
    
    def test_dynamic_reset_doesnt_affect_articulation(self):
        """Test that @reset only affects dynamics, not articulation."""
        events = [
            Articulation(type='legato'),
            DynamicLevel(level='f'),
            Note(pitches=[('c', 4, None)], duration=4),
            Reset(type='dynamic'),  # Only pops dynamics
            Note(pitches=[('d', 4, None)], duration=4),
        ]
        instrument = Instrument(name='piano', events=[], voices={1: events})
        seq = Sequence(events=[instrument])
        
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(seq)
        
        processed_events = result.events[0].voices[1]
        
        # Second note should have legato articulation but mf dynamic (system default)
        assert processed_events[4].articulation == 'legato'
        assert processed_events[4].dynamic_level == 'mf'
    
    def test_interleaved_articulation_and_dynamic_changes(self):
        """Test that articulation and dynamic changes maintain separate stacks."""
        events = [
            Articulation(type='staccato'),
            DynamicLevel(level='p'),
            Articulation(type='legato'),
            DynamicLevel(level='f'),
            Reset(type='articulation'),  # Back to staccato
            Note(pitches=[('c', 4, None)], duration=4),
            Reset(type='dynamic'),  # Back to p
            Note(pitches=[('d', 4, None)], duration=4),
        ]
        instrument = Instrument(name='piano', events=[], voices={1: events})
        seq = Sequence(events=[instrument])
        
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(seq)
        
        processed_events = result.events[0].voices[1]
        
        # First note: staccato (after articulation reset) + f (not yet reset)
        assert processed_events[5].articulation == 'staccato'
        assert processed_events[5].dynamic_level == 'f'
        
        # Second note: staccato (unchanged) + p (after dynamic reset)
        assert processed_events[7].articulation == 'staccato'
        assert processed_events[7].dynamic_level == 'p'


class TestVoiceIndependence:
    """Test that different voices maintain independent stacks."""
    
    def test_voices_have_separate_stacks(self):
        """Test that V1 and V2 have independent articulation stacks."""
        v1_events = [
            Articulation(type='staccato'),
            Note(pitches=[('c', 4, None)], duration=4),
        ]
        v2_events = [
            Articulation(type='legato'),
            Note(pitches=[('e', 4, None)], duration=4),
        ]
        instrument = Instrument(name='piano', events=[], voices={1: v1_events, 2: v2_events})
        seq = Sequence(events=[instrument])
        
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(seq)
        
        v1_processed = result.events[0].voices[1]
        v2_processed = result.events[0].voices[2]
        
        # V1 should have staccato
        assert v1_processed[1].articulation == 'staccato'
        
        # V2 should have legato (independent stack)
        assert v2_processed[1].articulation == 'legato'


class TestScopeInitialization:
    """Test that composition and instrument defaults pre-populate stacks."""
    
    def test_composition_defaults_on_stack(self):
        """Test that composition-level defaults are pushed to stack."""
        instrument = Instrument(
            name='piano',
            events=[],
            voices={1: [
                Note(pitches=[('c', 4, None)], duration=4),
                Reset(type='articulation'),  # Should pop to system default (no composition default)
                Note(pitches=[('d', 4, None)], duration=4),
            ]}
        )
        seq = Sequence(
            events=[instrument],
            composition_defaults={'articulation': 'legato'}  # Composition-level
        )
        
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(seq)
        
        processed_events = result.events[0].voices[1]
        
        # First note inherits composition default (legato)
        assert processed_events[0].articulation == 'legato'
        
        # After reset, should be at natural (system default, below composition default)
        assert processed_events[2].articulation == 'natural'
    
    def test_instrument_defaults_on_stack(self):
        """Test that instrument-level defaults are pushed to stack."""
        instrument = Instrument(
            name='piano',
            events=[],
            voices={1: [
                Note(pitches=[('c', 4, None)], duration=4),
                Reset(type='articulation'),  # Should pop to composition default
                Note(pitches=[('d', 4, None)], duration=4),
            ]},
            defaults_sequence=[(1, {'articulation': 'staccato'})]  # Instrument-level for V1
        )
        seq = Sequence(
            events=[instrument],
            composition_defaults={'articulation': 'legato'}  # Composition-level
        )
        
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(seq)
        
        processed_events = result.events[0].voices[1]
        
        # First note inherits instrument default (staccato)
        assert processed_events[0].articulation == 'staccato'
        
        # After reset, should be at legato (composition default, below instrument default)
        assert processed_events[2].articulation == 'legato'
    
    def test_full_scope_chain_in_stack(self):
        """Test that all three scope levels are in the stack: system < composition < instrument."""
        instrument = Instrument(
            name='piano',
            events=[],
            voices={1: [
                Articulation(type='tenuto'),  # Voice-level
                Note(pitches=[('c', 4, None)], duration=4),
                Reset(type='articulation'),  # Back to instrument
                Note(pitches=[('d', 4, None)], duration=4),
                Reset(type='articulation'),  # Back to composition
                Note(pitches=[('e', 4, None)], duration=4),
                Reset(type='articulation'),  # Back to system
                Note(pitches=[('f', 4, None)], duration=4),
            ]},
            defaults_sequence=[(1, {'articulation': 'staccato'})]
        )
        seq = Sequence(
            events=[instrument],
            composition_defaults={'articulation': 'legato'}
        )
        
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(seq)
        
        processed_events = result.events[0].voices[1]
        
        # After voice-level change: tenuto
        assert processed_events[1].articulation == 'tenuto'
        
        # After 1 reset: staccato (instrument)
        assert processed_events[3].articulation == 'staccato'
        
        # After 2 resets: legato (composition)
        assert processed_events[5].articulation == 'legato'
        
        # After 3 resets: natural (system)
        assert processed_events[7].articulation == 'natural'


class TestEdgeCases:
    """Test edge cases for stack-based reset."""
    
    def test_reset_at_system_default_is_noop(self):
        """Test that resetting when only system default remains is a no-op."""
        events = [
            Note(pitches=[('c', 4, None)], duration=4),  # natural (system default)
            Reset(type='articulation'),  # No-op, already at bottom
            Note(pitches=[('d', 4, None)], duration=4),  # Still natural
        ]
        instrument = Instrument(name='piano', events=[], voices={1: events})
        seq = Sequence(events=[instrument])
        
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(seq)
        
        processed_events = result.events[0].voices[1]
        
        # Both notes should be natural
        assert processed_events[0].articulation == 'natural'
        assert processed_events[2].articulation == 'natural'
    
    def test_multiple_consecutive_resets(self):
        """Test multiple consecutive resets work correctly."""
        events = [
            Articulation(type='staccato'),
            Articulation(type='legato'),
            Note(pitches=[('c', 4, None)], duration=4),  # legato
            Reset(type='articulation'),
            Reset(type='articulation'),  # Second reset immediately after first
            Note(pitches=[('d', 4, None)], duration=4),  # natural
        ]
        instrument = Instrument(name='piano', events=[], voices={1: events})
        seq = Sequence(events=[instrument])
        
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(seq)
        
        processed_events = result.events[0].voices[1]
        
        # First note: legato
        assert processed_events[2].articulation == 'legato'
        
        # After two resets: natural (system default)
        assert processed_events[5].articulation == 'natural'
    
    def test_reset_clears_crescendo_transition(self):
        """Test that @reset clears active crescendo/diminuendo."""
        events = [
            DynamicLevel(level='p'),
            DynamicTransition(type='crescendo'),
            Note(pitches=[('c', 4, None)], duration=4),  # Crescendo active
            Reset(type='dynamic'),  # Should clear transition
            Note(pitches=[('d', 4, None)], duration=4),
        ]
        instrument = Instrument(name='piano', events=[], voices={1: events})
        seq = Sequence(events=[instrument])
        
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(seq)
        
        processed_events = result.events[0].voices[1]
        
        # First note during crescendo should have increasing velocity
        # Second note after reset should be back at mf (system default)
        # The exact velocity would depend on crescendo implementation,
        # but we can verify the dynamic level
        assert processed_events[4].dynamic_level == 'mf'


class TestMeasurePersistence:
    """Test that stacks persist across measure boundaries."""
    
    def test_stack_persists_across_measures(self):
        """Test that articulation stack persists across measure boundaries."""
        measure1_events = [
            Articulation(type='staccato'),
            Note(pitches=[('c', 4, None)], duration=4),
            Note(pitches=[('d', 4, None)], duration=4),
            Note(pitches=[('e', 4, None)], duration=4),
            Note(pitches=[('f', 4, None)], duration=4),
        ]
        measure2_events = [
            Note(pitches=[('g', 4, None)], duration=4),  # Should still be staccato
            Reset(type='articulation'),
            Note(pitches=[('a', 4, None)], duration=4),  # Should be natural
            Note(pitches=[('b', 4, None)], duration=4),
            Note(pitches=[('c', 5, None)], duration=4),
        ]
        
        voice_events = [
            Measure(events=measure1_events),
            Measure(events=measure2_events),
        ]
        
        instrument = Instrument(name='piano', events=[], voices={1: voice_events})
        seq = Sequence(events=[instrument])
        
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(seq)
        
        processed_measures = result.events[0].voices[1]
        
        # Note in first measure: staccato
        assert processed_measures[0].events[1].articulation == 'staccato'
        
        # First note in second measure: still staccato (persists)
        assert processed_measures[1].events[0].articulation == 'staccato'
        
        # Second note in second measure (after reset): natural
        assert processed_measures[1].events[2].articulation == 'natural'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
