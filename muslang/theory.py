"""
Music Theory Support
Handles key signatures, scales, and ornament expansion.
"""

from typing import List, Optional, Tuple
from muslang.ast_nodes import Note, KeySignature


# Major key signatures (sharps and flats)
MAJOR_KEY_SIGNATURES = {
    # Sharp keys
    'c': [],
    'g': ['f'],
    'd': ['f', 'c'],
    'a': ['f', 'c', 'g'],
    'e': ['f', 'c', 'g', 'd'],
    'b': ['f', 'c', 'g', 'd', 'a'],
    # Flat keys
    'f': [('b', 'flat')],
    'b-': [('b', 'flat'), ('e', 'flat')],
    'e-': [('b', 'flat'), ('e', 'flat'), ('a', 'flat')],
    'a-': [('b', 'flat'), ('e', 'flat'), ('a', 'flat'), ('d', 'flat')],
    'd-': [('b', 'flat'), ('e', 'flat'), ('a', 'flat'), ('d', 'flat'), ('g', 'flat')],
    'g-': [('b', 'flat'), ('e', 'flat'), ('a', 'flat'), ('d', 'flat'), ('g', 'flat'), ('c', 'flat')],
}

# Minor key signatures (relative to major)
MINOR_KEY_SIGNATURES = {
    # Sharp keys
    'a': [],
    'e': ['f'],
    'b': ['f', 'c'],
    'f+': ['f', 'c', 'g'],
    'c+': ['f', 'c', 'g', 'd'],
    'g+': ['f', 'c', 'g', 'd', 'a'],
    # Flat keys  
    'd': [('b', 'flat')],
    'g': [('b', 'flat'), ('e', 'flat')],
    'c': [('b', 'flat'), ('e', 'flat'), ('a', 'flat')],
    'f': [('b', 'flat'), ('e', 'flat'), ('a', 'flat'), ('d', 'flat')],
    'b-': [('b', 'flat'), ('e', 'flat'), ('a', 'flat'), ('d', 'flat'), ('g', 'flat')],
    'e-': [('b', 'flat'), ('e', 'flat'), ('a', 'flat'), ('d', 'flat'), ('g', 'flat'), ('c', 'flat')],
}

# Scale intervals (semitones from root)
MAJOR_SCALE_INTERVALS = [0, 2, 4, 5, 7, 9, 11]
MINOR_SCALE_INTERVALS = [0, 2, 3, 5, 7, 8, 10]  # Natural minor

# Pitch class to semitone mapping
PITCH_TO_SEMITONE = {
    'c': 0, 'd': 2, 'e': 4, 'f': 5, 'g': 7, 'a': 9, 'b': 11
}


class KeySignatureInfo:
    """Information about a key signature and its accidentals"""
    
    def __init__(self, root: str, mode: str):
        """
        Initialize key signature info.
        
        Args:
            root: Root note (e.g., 'c', 'd', 'f', 'b-')
            mode: 'major' or 'minor'
        """
        self.root = root.lower()
        self.mode = mode.lower()
        self.accidentals = self._get_accidentals()
    
    def _get_accidentals(self) -> List[Tuple[str, str]]:
        """
        Get list of accidentals for this key.
        
        Returns:
            List of (pitch, accidental) tuples, e.g., [('f', 'sharp'), ('c', 'sharp')]
        """
        if self.mode == 'major':
            key_sig = MAJOR_KEY_SIGNATURES.get(self.root, [])
        else:
            key_sig = MINOR_KEY_SIGNATURES.get(self.root, [])
        
        # Normalize format
        accidentals = []
        for item in key_sig:
            if isinstance(item, tuple):
                accidentals.append(item)
            else:
                # String like 'f' means F sharp
                accidentals.append((item, 'sharp'))
        
        return accidentals
    
    def affects_pitch(self, pitch: str) -> bool:
        """Check if key signature affects this pitch"""
        pitch = pitch.lower()
        for acc_pitch, _ in self.accidentals:
            if acc_pitch == pitch:
                return True
        return False
    
    def get_accidental(self, pitch: str) -> Optional[str]:
        """
        Get accidental for pitch in this key.
        
        Returns:
            'sharp', 'flat', or None
        """
        pitch = pitch.lower()
        for acc_pitch, accidental in self.accidentals:
            if acc_pitch == pitch:
                return accidental
        return None
    
    def __repr__(self):
        return f"KeySignatureInfo({self.root} {self.mode}, {self.accidentals})"


def get_upper_neighbor(note: Note, key_sig: Optional[KeySignatureInfo] = None) -> Note:
    """
    Get the upper scale neighbor of a note.
    
    Args:
        note: The base note
        key_sig: Optional key signature context
    
    Returns:
        A new Note representing the upper neighbor
    """
    # Get next pitch in scale
    pitches = ['c', 'd', 'e', 'f', 'g', 'a', 'b']
    current_index = pitches.index(note.pitch)
    next_index = (current_index + 1) % 7
    next_pitch = pitches[next_index]
    
    # Determine octave
    next_octave = note.octave
    if next_index == 0:  # Wrapped around to C
        next_octave += 1
    
    # Apply key signature if present
    accidental = None
    if key_sig and key_sig.affects_pitch(next_pitch):
        accidental = key_sig.get_accidental(next_pitch)
    
    return Note(
        pitch=next_pitch,
        octave=next_octave,
        duration=32,  # Grace note duration
        accidental=accidental
    )


def get_lower_neighbor(note: Note, key_sig: Optional[KeySignatureInfo] = None) -> Note:
    """
    Get the lower scale neighbor of a note.
    
    Args:
        note: The base note
        key_sig: Optional key signature context
    
    Returns:
        A new Note representing the lower neighbor
    """
    # Get previous pitch in scale
    pitches = ['c', 'd', 'e', 'f', 'g', 'a', 'b']
    current_index = pitches.index(note.pitch)
    prev_index = (current_index - 1) % 7
    prev_pitch = pitches[prev_index]
    
    # Determine octave
    prev_octave = note.octave
    if prev_index == 6:  # Wrapped around to B
        prev_octave -= 1
    
    # Apply key signature if present
    accidental = None
    if key_sig and key_sig.affects_pitch(prev_pitch):
        accidental = key_sig.get_accidental(prev_pitch)
    
    return Note(
        pitch=prev_pitch,
        octave=prev_octave,
        duration=32,  # Grace note duration
        accidental=accidental
    )


def expand_ornament(ornament_type: str, note: Note, 
                   key_sig: Optional[KeySignatureInfo] = None) -> List[Note]:
    """
    Expand an ornament into a sequence of notes.
    
    Args:
        ornament_type: 'trill', 'mordent', or 'turn'
        note: The main note to ornament
        key_sig: Optional key signature context
    
    Returns:
        List of notes representing the ornament
    """
    if ornament_type == 'trill':
        # Trill: alternating main note and upper neighbor
        # Generate 8 fast notes (32nd notes)
        upper = get_upper_neighbor(note, key_sig)
        trill_notes = []
        
        for i in range(8):
            if i % 2 == 0:
                # Main note
                trill_notes.append(Note(
                    pitch=note.pitch,
                    octave=note.octave,
                    duration=32,
                    accidental=note.accidental
                ))
            else:
                # Upper neighbor
                trill_notes.append(upper)
        
        return trill_notes
    
    elif ornament_type == 'mordent':
        # Mordent: main note, lower neighbor, main note
        lower = get_lower_neighbor(note, key_sig)
        
        return [
            Note(pitch=note.pitch, octave=note.octave, duration=32, 
                 accidental=note.accidental),
            lower,
            Note(pitch=note.pitch, octave=note.octave, 
                 duration=note.duration, accidental=note.accidental),
        ]
    
    elif ornament_type == 'turn':
        # Turn: upper neighbor, main note, lower neighbor, main note
        upper = get_upper_neighbor(note, key_sig)
        lower = get_lower_neighbor(note, key_sig)
        
        return [
            upper,
            Note(pitch=note.pitch, octave=note.octave, duration=32, 
                 accidental=note.accidental),
            lower,
            Note(pitch=note.pitch, octave=note.octave, 
                 duration=note.duration, accidental=note.accidental),
        ]
    
    else:
        # Unknown ornament type, return original note
        return [note]


def apply_key_signature_to_note(note: Note, key_sig: KeySignatureInfo) -> Note:
    """
    Apply key signature to a note if it doesn't have explicit accidental.
    
    Args:
        note: The note to process
        key_sig: The key signature to apply
    
    Returns:
        A new Note with key signature accidental applied (if needed)
    """
    # If note already has an explicit accidental, don't override
    if note.accidental is not None:
        return note
    
    # Check if key signature affects this pitch
    if key_sig.affects_pitch(note.pitch):
        accidental = key_sig.get_accidental(note.pitch)
        # Create new note with accidental
        from dataclasses import replace
        return replace(note, accidental=accidental)
    
    return note
