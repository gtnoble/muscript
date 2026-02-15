"""
Articulation Mapping System

Maps articulations and dynamics to MIDI parameters (velocity, duration, CC).
Tracks state and provides methods for calculating note-level MIDI values.
"""

from dataclasses import dataclass
from typing import Optional
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


@dataclass
class ArticulationState:
    """Current articulation state"""
    type: str = 'natural'
    duration_percent: int = NATURAL_DURATION_PERCENT


@dataclass
class DynamicState:
    """Current dynamic state"""
    level: str = 'mf'
    velocity: int = VELOCITY_MF
    transition_active: Optional[str] = None  # 'crescendo' or 'diminuendo'
    transition_start_velocity: Optional[int] = None
    transition_target_velocity: Optional[int] = None


class ArticulationMapper:
    """Maps articulations and dynamics to MIDI parameters"""
    
    def __init__(self):
        self.artic_state = ArticulationState()
        self.dynamic_state = DynamicState()
    
    def process_articulation(self, artic_type: str):
        """Update articulation state"""
        if artic_type == 'staccato':
            self.artic_state.type = 'staccato'
            self.artic_state.duration_percent = STACCATO_DURATION
        elif artic_type == 'legato':
            self.artic_state.type = 'legato'
            self.artic_state.duration_percent = LEGATO_DURATION
        elif artic_type == 'tenuto':
            self.artic_state.type = 'tenuto'
            self.artic_state.duration_percent = TENUTO_DURATION
        elif artic_type == 'marcato':
            self.artic_state.type = 'marcato'
            self.artic_state.duration_percent = MARCATO_DURATION
    
    def process_reset(self, reset_type: str = 'natural'):
        """Reset articulation and/or dynamics"""
        if reset_type == 'natural':
            # Reset articulation only
            self.artic_state = ArticulationState()
        elif reset_type == 'full':
            # Reset both
            self.artic_state = ArticulationState()
            self.dynamic_state = DynamicState()
    
    def process_dynamic_level(self, level: str):
        """Update dynamic level"""
        velocity_map = {
            'pp': VELOCITY_PP,
            'p': VELOCITY_P,
            'mp': VELOCITY_MP,
            'mf': VELOCITY_MF,
            'f': VELOCITY_F,
            'ff': VELOCITY_FF,
        }
        self.dynamic_state.level = level
        self.dynamic_state.velocity = velocity_map[level]
        # Set target velocity for potential transitions
        self.dynamic_state.transition_target_velocity = velocity_map[level]
    
    def process_dynamic_transition(self, trans_type: str, target_level: Optional[str] = None):
        """Start crescendo or diminuendo
        
        Args:
            trans_type: 'crescendo', 'diminuendo', or 'decresc'
            target_level: Optional target dynamic level (e.g., 'f' for crescendo to forte)
        """
        # Normalize decresc to diminuendo
        if trans_type == 'decresc':
            trans_type = 'diminuendo'
        
        self.dynamic_state.transition_active = trans_type
        self.dynamic_state.transition_start_velocity = self.dynamic_state.velocity
        
        # Set target velocity
        if target_level:
            velocity_map = {
                'pp': VELOCITY_PP,
                'p': VELOCITY_P,
                'mp': VELOCITY_MP,
                'mf': VELOCITY_MF,
                'f': VELOCITY_F,
                'ff': VELOCITY_FF,
            }
            self.dynamic_state.transition_target_velocity = velocity_map.get(target_level, VELOCITY_FF if trans_type == 'crescendo' else VELOCITY_PP)
        else:
            # Default targets if not specified
            if trans_type == 'crescendo':
                self.dynamic_state.transition_target_velocity = VELOCITY_FF
            else:
                self.dynamic_state.transition_target_velocity = VELOCITY_PP
    
    def end_dynamic_transition(self):
        """End the current dynamic transition"""
        self.dynamic_state.transition_active = None
        self.dynamic_state.transition_start_velocity = None
    
    def get_note_duration(self, base_duration_ticks: int) -> int:
        """Calculate actual note duration based on articulation
        
        Args:
            base_duration_ticks: The full duration in MIDI ticks
        
        Returns:
            Actual duration to use for note-on to note-off
        """
        return int(base_duration_ticks * self.artic_state.duration_percent / 100)
    
    def get_note_velocity(self, accent_type: Optional[str] = None) -> int:
        """Calculate note velocity based on dynamic state and accents
        
        Args:
            accent_type: Optional one-shot accent ('sforzando', 'forte-piano', 'marcato')
        
        Returns:
            MIDI velocity (0-127)
        """
        velocity = self.dynamic_state.velocity
        
        # Apply one-shot accents
        if accent_type == 'sforzando':
            velocity = min(127, velocity + SFORZANDO_BOOST)
        elif accent_type == 'forte-piano':
            velocity = min(127, velocity + FORTE_PIANO_BOOST)
        elif accent_type == 'marcato':
            # Marcato is both an articulation and has accent quality
            velocity = min(127, velocity + MARCATO_BOOST)
        
        # Apply crescendo/diminuendo progression
        if self.dynamic_state.transition_active:
            target = self.dynamic_state.transition_target_velocity
            
            if self.dynamic_state.transition_active == 'crescendo':
                # Increase velocity gradually
                if self.dynamic_state.velocity < target:
                    self.dynamic_state.velocity = min(
                        target,
                        self.dynamic_state.velocity + DYNAMIC_TRANSITION_STEP
                    )
            elif self.dynamic_state.transition_active == 'diminuendo':
                # Decrease velocity gradually
                if self.dynamic_state.velocity > target:
                    self.dynamic_state.velocity = max(
                        target,
                        self.dynamic_state.velocity - DYNAMIC_TRANSITION_STEP
                    )
            
            velocity = self.dynamic_state.velocity
        
        # Ensure velocity stays in valid range
        return min(127, max(0, velocity))
    
    def should_add_legato_cc(self) -> bool:
        """Check if legato CC#68 should be sent"""
        return self.artic_state.type == 'legato'
    
    def get_current_articulation(self) -> str:
        """Get current articulation type"""
        return self.artic_state.type
    
    def get_current_dynamic_level(self) -> str:
        """Get current dynamic level"""
        return self.dynamic_state.level
    
    def is_in_transition(self) -> bool:
        """Check if currently in a dynamic transition"""
        return self.dynamic_state.transition_active is not None
