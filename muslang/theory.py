"""
Music Theory Support
Handles key signatures, scales, and ornament expansion.
"""

from typing import List, Optional, Tuple, Dict
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

ALLOWED_DURATIONS = [1, 2, 4, 8, 16, 32, 64]
UNITS_TO_DURATION: Dict[int, Tuple[int, bool]] = {}
for _duration in ALLOWED_DURATIONS:
    base_units = 128 // _duration
    UNITS_TO_DURATION[base_units] = (_duration, False)
    dotted_units = (base_units * 3) // 2
    UNITS_TO_DURATION[dotted_units] = (_duration, True)


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
    total_units = _note_to_units(note)
    if total_units <= 0:
        return [note]

    if ornament_type == 'trill':
        upper = get_upper_neighbor(note, key_sig)
        return _expand_trill(note, upper, total_units)

    elif ornament_type == 'mordent':
        lower = get_lower_neighbor(note, key_sig)
        return _expand_mordent(note, lower, total_units)

    elif ornament_type == 'turn':
        upper = get_upper_neighbor(note, key_sig)
        lower = get_lower_neighbor(note, key_sig)
        return _expand_turn(note, upper, lower, total_units)

    elif ornament_type == 'tremolo':
        return _expand_tremolo(note, total_units)
    
    else:
        # Unknown ornament type, return original note
        return [note]


def _note_to_units(note: Note) -> int:
    """Convert note duration to 1/128-whole-note units."""
    duration = note.duration if note.duration else 4
    base_units = 128 // duration
    if note.dotted:
        return (base_units * 3) // 2
    return base_units


def _units_to_duration(units: int) -> Optional[Tuple[int, bool]]:
    """Convert 1/128 units to (duration, dotted) if representable."""
    return UNITS_TO_DURATION.get(units)


def _build_note(base_note: Note, pitch: str, octave: int, accidental: Optional[str], units: int) -> Note:
    """Create a note matching base properties with duration from units."""
    duration_info = _units_to_duration(units)
    if duration_info is None:
        raise ValueError(f"Cannot represent note duration units={units}")
    duration, dotted = duration_info
    return Note(
        pitch=pitch,
        octave=octave,
        duration=duration,
        dotted=dotted,
        accidental=accidental,
    )


def _principal_from_units(note: Note, units: int) -> List[Note]:
    """Fallback to principal note with exact represented duration units."""
    duration_info = _units_to_duration(units)
    if duration_info is None:
        return [note]
    duration, dotted = duration_info
    return [
        Note(
            pitch=note.pitch,
            octave=note.octave,
            duration=duration,
            dotted=dotted,
            accidental=note.accidental,
        )
    ]


def _expand_trill(note: Note, upper: Note, total_units: int) -> List[Note]:
    """Expand trill into alternating principal/upper notes across full duration."""
    segment_units = 4 if total_units >= 4 else 2
    if total_units < segment_units:
        return _principal_from_units(note, total_units)

    count = total_units // segment_units
    remainder = total_units % segment_units
    notes: List[Note] = []

    for i in range(count):
        if i % 2 == 0:
            notes.append(_build_note(note, note.pitch, note.octave, note.accidental, segment_units))
        else:
            notes.append(_build_note(note, upper.pitch, upper.octave, upper.accidental, segment_units))

    if remainder > 0:
        if _units_to_duration(remainder) is None:
            return _principal_from_units(note, total_units)
        notes.append(_build_note(note, note.pitch, note.octave, note.accidental, remainder))

    return notes if notes else _principal_from_units(note, total_units)


def _expand_mordent(note: Note, lower: Note, total_units: int) -> List[Note]:
    """Expand mordent as principal-lower-principal across full duration."""
    for short_units in (4, 2):
        remaining_units = total_units - (2 * short_units)
        if remaining_units < 2:
            continue
        if _units_to_duration(remaining_units) is None:
            continue

        return [
            _build_note(note, note.pitch, note.octave, note.accidental, short_units),
            _build_note(note, lower.pitch, lower.octave, lower.accidental, short_units),
            _build_note(note, note.pitch, note.octave, note.accidental, remaining_units),
        ]

    return _principal_from_units(note, total_units)


def _expand_turn(note: Note, upper: Note, lower: Note, total_units: int) -> List[Note]:
    """Expand turn as upper-principal-lower-principal across full duration."""
    base = total_units // 4
    remainder = total_units % 4
    parts = [base, base, base, base]

    # Keep later notes slightly longer when duration doesn't divide by 4 evenly.
    for i in range(remainder):
        parts[-(i + 1)] += 1

    if any(part < 2 or _units_to_duration(part) is None for part in parts):
        return _principal_from_units(note, total_units)

    return [
        _build_note(note, upper.pitch, upper.octave, upper.accidental, parts[0]),
        _build_note(note, note.pitch, note.octave, note.accidental, parts[1]),
        _build_note(note, lower.pitch, lower.octave, lower.accidental, parts[2]),
        _build_note(note, note.pitch, note.octave, note.accidental, parts[3]),
    ]


def _expand_tremolo(note: Note, total_units: int) -> List[Note]:
    """Expand tremolo as rapid principal-note repetitions across full duration."""
    segment_units = 8 if total_units >= 8 else 4 if total_units >= 4 else 2
    if total_units < segment_units:
        return _principal_from_units(note, total_units)

    count = total_units // segment_units
    remainder = total_units % segment_units
    notes = [
        _build_note(note, note.pitch, note.octave, note.accidental, segment_units)
        for _ in range(count)
    ]

    if remainder > 0:
        if _units_to_duration(remainder) is None:
            return _principal_from_units(note, total_units)
        notes.append(_build_note(note, note.pitch, note.octave, note.accidental, remainder))

    return notes if notes else _principal_from_units(note, total_units)


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
