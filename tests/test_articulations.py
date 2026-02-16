"""
Unit tests for articulation mapping system
"""

import pytest
from muslang.articulations import ArticulationMapper, ArticulationState, DynamicState
from muslang.config import (
    NATURAL_DURATION_PERCENT,
    STACCATO_DURATION,
    LEGATO_DURATION,
    TENUTO_DURATION,
    MARCATO_DURATION,
    VELOCITY_PP,
    VELOCITY_P,
    VELOCITY_MP,
    VELOCITY_MF,
    VELOCITY_F,
    VELOCITY_FF,
    SFORZANDO_BOOST,
    MARCATO_BOOST,
    FORTE_PIANO_BOOST,
    DYNAMIC_TRANSITION_STEP,
)


class TestArticulationState:
    """Test ArticulationState dataclass"""
    
    def test_default_state(self):
        state = ArticulationState()
        assert state.type == 'natural'
        assert state.duration_percent == NATURAL_DURATION_PERCENT
    
    def test_custom_state(self):
        state = ArticulationState(type='staccato', duration_percent=50)
        assert state.type == 'staccato'
        assert state.duration_percent == 50


class TestDynamicState:
    """Test DynamicState dataclass"""
    
    def test_default_state(self):
        state = DynamicState()
        assert state.level == 'mf'
        assert state.velocity == VELOCITY_MF
        assert state.transition_active is None
        assert state.transition_start_velocity is None
        assert state.transition_target_velocity is None
    
    def test_custom_state(self):
        state = DynamicState(
            level='f',
            velocity=VELOCITY_F,
            transition_active='crescendo',
            transition_start_velocity=70,
            transition_target_velocity=100
        )
        assert state.level == 'f'
        assert state.velocity == VELOCITY_F
        assert state.transition_active == 'crescendo'
        assert state.transition_start_velocity == 70
        assert state.transition_target_velocity == 100


class TestArticulationMapper:
    """Test ArticulationMapper class"""
    
    def test_initial_state(self):
        mapper = ArticulationMapper()
        assert mapper.artic_state.type == 'natural'
        assert mapper.dynamic_state.level == 'mf'
        assert mapper.get_current_articulation() == 'natural'
        assert mapper.get_current_dynamic_level() == 'mf'
    
    def test_process_staccato(self):
        mapper = ArticulationMapper()
        mapper.process_articulation('staccato')
        assert mapper.artic_state.type == 'staccato'
        assert mapper.artic_state.duration_percent == STACCATO_DURATION
    
    def test_process_legato(self):
        mapper = ArticulationMapper()
        mapper.process_articulation('legato')
        assert mapper.artic_state.type == 'legato'
        assert mapper.artic_state.duration_percent == LEGATO_DURATION
        assert mapper.should_add_legato_cc()
    
    def test_process_tenuto(self):
        mapper = ArticulationMapper()
        mapper.process_articulation('tenuto')
        assert mapper.artic_state.type == 'tenuto'
        assert mapper.artic_state.duration_percent == TENUTO_DURATION
    
    def test_process_marcato(self):
        mapper = ArticulationMapper()
        mapper.process_articulation('marcato')
        assert mapper.artic_state.type == 'marcato'
        assert mapper.artic_state.duration_percent == MARCATO_DURATION
    
    def test_reset_natural(self):
        mapper = ArticulationMapper()
        mapper.process_articulation('staccato')
        mapper.process_dynamic_level('ff')
        
        mapper.process_reset('articulation')
        
        # Articulation reset
        assert mapper.artic_state.type == 'natural'
        assert mapper.artic_state.duration_percent == NATURAL_DURATION_PERCENT
        
        # Dynamics NOT reset
        assert mapper.dynamic_state.level == 'ff'
    
    def test_reset_full(self):
        mapper = ArticulationMapper()
        mapper.process_articulation('staccato')
        mapper.process_dynamic_level('ff')
        
        mapper.process_reset('dynamic')
        
        # Articulation NOT reset
        assert mapper.artic_state.type == 'staccato'
        # Dynamics reset
        assert mapper.dynamic_state.level == 'mf'


class TestDynamicLevels:
    """Test dynamic level processing"""
    
    def test_pianissimo(self):
        mapper = ArticulationMapper()
        mapper.process_dynamic_level('pp')
        assert mapper.dynamic_state.level == 'pp'
        assert mapper.dynamic_state.velocity == VELOCITY_PP
    
    def test_piano(self):
        mapper = ArticulationMapper()
        mapper.process_dynamic_level('p')
        assert mapper.dynamic_state.level == 'p'
        assert mapper.dynamic_state.velocity == VELOCITY_P
    
    def test_mezzo_piano(self):
        mapper = ArticulationMapper()
        mapper.process_dynamic_level('mp')
        assert mapper.dynamic_state.level == 'mp'
        assert mapper.dynamic_state.velocity == VELOCITY_MP
    
    def test_mezzo_forte(self):
        mapper = ArticulationMapper()
        mapper.process_dynamic_level('mf')
        assert mapper.dynamic_state.level == 'mf'
        assert mapper.dynamic_state.velocity == VELOCITY_MF
    
    def test_forte(self):
        mapper = ArticulationMapper()
        mapper.process_dynamic_level('f')
        assert mapper.dynamic_state.level == 'f'
        assert mapper.dynamic_state.velocity == VELOCITY_F
    
    def test_fortissimo(self):
        mapper = ArticulationMapper()
        mapper.process_dynamic_level('ff')
        assert mapper.dynamic_state.level == 'ff'
        assert mapper.dynamic_state.velocity == VELOCITY_FF


class TestDynamicTransitions:
    """Test crescendo and diminuendo"""
    
    def test_start_crescendo(self):
        mapper = ArticulationMapper()
        mapper.process_dynamic_level('p')
        mapper.process_dynamic_transition('crescendo')
        
        assert mapper.dynamic_state.transition_active == 'crescendo'
        assert mapper.is_in_transition()
        assert mapper.dynamic_state.transition_target_velocity == VELOCITY_FF
    
    def test_start_diminuendo(self):
        mapper = ArticulationMapper()
        mapper.process_dynamic_level('f')
        mapper.process_dynamic_transition('diminuendo')
        
        assert mapper.dynamic_state.transition_active == 'diminuendo'
        assert mapper.is_in_transition()
        assert mapper.dynamic_state.transition_target_velocity == VELOCITY_PP
    
    def test_decresc_alias(self):
        mapper = ArticulationMapper()
        mapper.process_dynamic_transition('decresc')
        
        # Should normalize to diminuendo
        assert mapper.dynamic_state.transition_active == 'diminuendo'
    
    def test_crescendo_progression(self):
        mapper = ArticulationMapper()
        mapper.process_dynamic_level('p')  # Start at piano (55)
        mapper.process_dynamic_transition('crescendo', 'f')  # Target forte (100)
        
        initial_velocity = mapper.dynamic_state.velocity
        
        # Generate several notes during crescendo
        velocities = []
        for _ in range(10):
            vel = mapper.get_note_velocity()
            velocities.append(vel)
        
        # Velocity should increase
        assert velocities[-1] > velocities[0]
        
        # Should reach or approach target
        assert velocities[-1] >= VELOCITY_F - DYNAMIC_TRANSITION_STEP
    
    def test_diminuendo_progression(self):
        mapper = ArticulationMapper()
        mapper.process_dynamic_level('f')  # Start at forte (100)
        mapper.process_dynamic_transition('diminuendo', 'p')  # Target piano (55)
        
        initial_velocity = mapper.dynamic_state.velocity
        
        # Generate several notes during diminuendo
        velocities = []
        for _ in range(10):
            vel = mapper.get_note_velocity()
            velocities.append(vel)
        
        # Velocity should decrease
        assert velocities[-1] < velocities[0]
        
        # Should reach or approach target
        assert velocities[-1] <= VELOCITY_P + DYNAMIC_TRANSITION_STEP
    
    def test_end_transition(self):
        mapper = ArticulationMapper()
        mapper.process_dynamic_transition('crescendo')
        mapper.end_dynamic_transition()
        
        assert mapper.dynamic_state.transition_active is None
        assert not mapper.is_in_transition()


class TestNoteDuration:
    """Test note duration calculation"""
    
    def test_natural_duration(self):
        mapper = ArticulationMapper()
        base_ticks = 480  # Quarter note at 480 PPQ
        actual = mapper.get_note_duration(base_ticks)
        expected = int(480 * NATURAL_DURATION_PERCENT / 100)
        assert actual == expected
    
    def test_staccato_duration(self):
        mapper = ArticulationMapper()
        mapper.process_articulation('staccato')
        base_ticks = 480
        actual = mapper.get_note_duration(base_ticks)
        expected = int(480 * STACCATO_DURATION / 100)
        assert actual == expected
        assert actual < int(480 * NATURAL_DURATION_PERCENT / 100)
    
    def test_legato_duration(self):
        mapper = ArticulationMapper()
        mapper.process_articulation('legato')
        base_ticks = 480
        actual = mapper.get_note_duration(base_ticks)
        expected = int(480 * LEGATO_DURATION / 100)
        assert actual == expected
        assert actual >= int(480 * NATURAL_DURATION_PERCENT / 100)
    
    def test_tenuto_duration(self):
        mapper = ArticulationMapper()
        mapper.process_articulation('tenuto')
        base_ticks = 480
        actual = mapper.get_note_duration(base_ticks)
        expected = int(480 * TENUTO_DURATION / 100)
        assert actual == expected
    
    def test_marcato_duration(self):
        mapper = ArticulationMapper()
        mapper.process_articulation('marcato')
        base_ticks = 480
        actual = mapper.get_note_duration(base_ticks)
        expected = int(480 * MARCATO_DURATION / 100)
        assert actual == expected


class TestNoteVelocity:
    """Test velocity calculation"""
    
    def test_base_velocity(self):
        mapper = ArticulationMapper()
        vel = mapper.get_note_velocity()
        assert vel == VELOCITY_MF  # Default
    
    def test_velocity_with_dynamic_level(self):
        mapper = ArticulationMapper()
        mapper.process_dynamic_level('pp')
        assert mapper.get_note_velocity() == VELOCITY_PP
        
        mapper.process_dynamic_level('ff')
        assert mapper.get_note_velocity() == VELOCITY_FF
    
    def test_sforzando_accent(self):
        mapper = ArticulationMapper()
        mapper.process_dynamic_level('mf')
        base_vel = mapper.get_note_velocity()
        sfz_vel = mapper.get_note_velocity(accent_type='sforzando')
        
        assert sfz_vel == base_vel + SFORZANDO_BOOST
    
    def test_marcato_accent(self):
        mapper = ArticulationMapper()
        mapper.process_dynamic_level('mf')
        base_vel = mapper.get_note_velocity()
        marcato_vel = mapper.get_note_velocity(accent_type='marcato')
        
        assert marcato_vel == base_vel + MARCATO_BOOST
    
    def test_forte_piano_accent(self):
        mapper = ArticulationMapper()
        mapper.process_dynamic_level('mf')
        base_vel = mapper.get_note_velocity()
        fp_vel = mapper.get_note_velocity(accent_type='forte-piano')
        
        assert fp_vel == base_vel + FORTE_PIANO_BOOST
    
    def test_velocity_clamp_max(self):
        mapper = ArticulationMapper()
        mapper.process_dynamic_level('ff')
        # Even with accent, should not exceed 127
        vel = mapper.get_note_velocity(accent_type='forte-piano')
        assert vel <= 127
    
    def test_velocity_clamp_min(self):
        mapper = ArticulationMapper()
        mapper.process_dynamic_level('pp')
        vel = mapper.get_note_velocity()
        assert vel >= 0


class TestLegatoCC:
    """Test legato CC detection"""
    
    def test_should_add_legato_cc_false(self):
        mapper = ArticulationMapper()
        assert not mapper.should_add_legato_cc()
        
        mapper.process_articulation('staccato')
        assert not mapper.should_add_legato_cc()
    
    def test_should_add_legato_cc_true(self):
        mapper = ArticulationMapper()
        mapper.process_articulation('legato')
        assert mapper.should_add_legato_cc()


class TestStateQueries:
    """Test state query methods"""
    
    def test_get_current_articulation(self):
        mapper = ArticulationMapper()
        assert mapper.get_current_articulation() == 'natural'
        
        mapper.process_articulation('staccato')
        assert mapper.get_current_articulation() == 'staccato'
    
    def test_get_current_dynamic_level(self):
        mapper = ArticulationMapper()
        assert mapper.get_current_dynamic_level() == 'mf'
        
        mapper.process_dynamic_level('p')
        assert mapper.get_current_dynamic_level() == 'p'
    
    def test_is_in_transition(self):
        mapper = ArticulationMapper()
        assert not mapper.is_in_transition()
        
        mapper.process_dynamic_transition('crescendo')
        assert mapper.is_in_transition()
        
        mapper.end_dynamic_transition()
        assert not mapper.is_in_transition()


class TestIntegrationScenarios:
    """Test realistic articulation scenarios"""
    
    def test_staccato_forte_passage(self):
        """Staccato notes at forte"""
        mapper = ArticulationMapper()
        mapper.process_articulation('staccato')
        mapper.process_dynamic_level('f')
        
        # Generate a few notes
        duration = mapper.get_note_duration(480)
        velocity = mapper.get_note_velocity()
        
        assert duration == int(480 * STACCATO_DURATION / 100)
        assert velocity == VELOCITY_F
    
    def test_legato_crescendo(self):
        """Legato phrase with crescendo"""
        mapper = ArticulationMapper()
        mapper.process_articulation('legato')
        mapper.process_dynamic_level('mp')
        mapper.process_dynamic_transition('crescendo', 'ff')
        
        assert mapper.should_add_legato_cc()
        assert mapper.is_in_transition()
        
        # Velocity should increase over time
        vel1 = mapper.get_note_velocity()
        vel2 = mapper.get_note_velocity()
        vel3 = mapper.get_note_velocity()
        
        assert vel1 <= vel2 <= vel3
    
    def test_accent_pattern(self):
        """Alternating accented and unaccented notes"""
        mapper = ArticulationMapper()
        mapper.process_dynamic_level('mf')
        
        normal = mapper.get_note_velocity()
        accented = mapper.get_note_velocity(accent_type='sforzando')
        normal2 = mapper.get_note_velocity()
        
        # Accent should be louder
        assert accented > normal
        # Normal notes should be same
        assert normal == normal2
    
    def test_articulation_change_midway(self):
        """Change articulation in middle of phrase"""
        mapper = ArticulationMapper()
        
        # Start with staccato
        mapper.process_articulation('staccato')
        dur1 = mapper.get_note_duration(480)
        
        # Switch to legato
        mapper.process_articulation('legato')
        dur2 = mapper.get_note_duration(480)
        
        # Durations should be different
        assert dur1 < dur2
        assert dur1 == int(480 * STACCATO_DURATION / 100)
        assert dur2 == int(480 * LEGATO_DURATION / 100)
    
    def test_dynamic_reset_during_crescendo(self):
        """Reset dynamics during crescendo"""
        mapper = ArticulationMapper()
        mapper.process_dynamic_level('p')
        mapper.process_dynamic_transition('crescendo')
        
        # Get a few velocities
        _ = mapper.get_note_velocity()
        _ = mapper.get_note_velocity()
        
        # Reset dynamics only
        mapper.process_reset('dynamic')
        
        # Dynamics should be reset, transition should be cleared
        assert not mapper.is_in_transition()
        assert mapper.get_current_dynamic_level() == 'mf'
        # Articulation unchanged
        assert mapper.get_current_articulation() == 'natural'
