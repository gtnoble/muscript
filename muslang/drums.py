"""
Percussion/drum mapping for General MIDI drum kit.

This module provides mappings from human-readable drum names
to General MIDI drum note numbers (used on channel 10).
"""

from typing import Dict

# General MIDI Drum Map (Channel 10)
# MIDI note numbers for standard drum kit
DRUM_MAP: Dict[str, int] = {
    # Bass drums
    'kick': 36,          # Bass Drum 1 (acoustic)
    'kick2': 35,         # Bass Drum 2
    
    # Snare drums
    'snare': 38,         # Acoustic Snare
    'snare2': 40,        # Electric Snare
    'rimshot': 37,       # Side Stick / Rimshot
    'clap': 39,          # Hand Clap
    
    # Hi-hats
    'hat': 42,           # Closed Hi-Hat
    'hihat': 42,         # Alias for closed hi-hat
    'openhat': 46,       # Open Hi-Hat
    'pedalhat': 44,      # Pedal Hi-Hat
    
    # Cymbals
    'crash': 49,         # Crash Cymbal 1
    'crash2': 57,        # Crash Cymbal 2
    'ride': 51,          # Ride Cymbal 1
    'ride2': 59,         # Ride Cymbal 2
    'splash': 55,        # Splash Cymbal
    'china': 52,         # Chinese Cymbal
    'ridebell': 53,      # Ride Bell
    
    # Toms
    'tom1': 48,          # Hi Tom (Hi Mid Tom)
    'tom2': 47,          # Low-Mid Tom
    'tom3': 45,          # Low Tom
    'tom4': 43,          # High Floor Tom
    'tom5': 41,          # Low Floor Tom
    'hightom': 50,       # High Tom
    'lowtom': 41,        # Low Floor Tom (alias)
    
    # Percussion
    'cowbell': 56,       # Cowbell
    'tambourine': 54,    # Tambourine
    'vibraslap': 58,     # Vibraslap
    'maracas': 70,       # Maracas
    'shaker': 82,        # Shaker
    'woodblock': 76,     # Hi Wood Block
    'woodblock2': 77,    # Low Wood Block
    'cabasa': 69,        # Cabasa
    'guiro': 73,         # Short Guiro (Guiro)
    'guiro2': 74,        # Long Guiro
    'claves': 75,        # Claves
    'triangle': 81,      # Open Triangle
    'triangle2': 80,     # Mute Triangle
    
    # Latin percussion
    'bongo': 60,         # Hi Bongo
    'bongo2': 61,        # Low Bongo
    'conga': 62,         # Mute Hi Conga
    'conga2': 63,        # Open Hi Conga
    'conga3': 64,        # Low Conga
    'timbale': 65,       # High Timbale
    'timbale2': 66,      # Low Timbale
    'agogo': 67,         # High Agogo
    'agogo2': 68,        # Low Agogo
    
    # Additional percussion
    'whistle': 71,       # Short Whistle
    'whistle2': 72,      # Long Whistle
    'cuica': 78,         # Mute Cuica
    'cuica2': 79,        # Open Cuica
    'bellcym': 83,       # Jingle Bell
}


def get_drum_midi_note(drum_name: str) -> int:
    """
    Get MIDI note number for a drum name.
    
    Args:
        drum_name: Human-readable drum name (e.g., 'kick', 'snare', 'hat')
    
    Returns:
        MIDI note number (0-127) for the drum sound
    
    Raises:
        ValueError: If drum_name is not recognized
    
    Examples:
        >>> get_drum_midi_note('kick')
        36
        >>> get_drum_midi_note('snare')
        38
        >>> get_drum_midi_note('hat')
        42
    """
    drum_name_lower = drum_name.lower()
    
    if drum_name_lower not in DRUM_MAP:
        available = ', '.join(sorted(DRUM_MAP.keys()))
        raise ValueError(
            f"Unknown drum name: '{drum_name}'. "
            f"Available drums: {available}"
        )
    
    return DRUM_MAP[drum_name_lower]


def is_percussion_instrument(instrument_name: str) -> bool:
    """
    Check if an instrument name refers to a percussion/drum kit.
    
    Percussion instruments use MIDI channel 10 (0-indexed channel 9)
    and map drum names to MIDI note numbers instead of pitched notes.
    
    Args:
        instrument_name: Name of the instrument
    
    Returns:
        True if the instrument is percussion, False otherwise
    
    Examples:
        >>> is_percussion_instrument('drums')
        True
        >>> is_percussion_instrument('Percussion')
        True
        >>> is_percussion_instrument('piano')
        False
    """
    return instrument_name.lower() in ['drums', 'percussion', 'kit', 'drumkit']


def get_all_drum_names() -> list[str]:
    """
    Get a sorted list of all available drum names.
    
    Returns:
        List of drum name strings
    
    Examples:
        >>> drums = get_all_drum_names()
        >>> 'kick' in drums
        True
        >>> 'snare' in drums
        True
    """
    return sorted(DRUM_MAP.keys())


def validate_drum_name(drum_name: str) -> bool:
    """
    Check if a drum name is valid without raising an exception.
    
    Args:
        drum_name: Drum name to validate
    
    Returns:
        True if valid, False otherwise
    
    Examples:
        >>> validate_drum_name('kick')
        True
        >>> validate_drum_name('invalid')
        False
    """
    return drum_name.lower() in DRUM_MAP
