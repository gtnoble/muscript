"""
MIDI Generation Module

Generates MIDI files from analyzed AST. Handles:
- MIDI event generation (note on/off, CC, meta-events)
- Instrument and channel management
- Articulation and dynamic state tracking
- Advanced features (slurs, slides, percussion)
- Timing and velocity calculations
"""

from midiutil import MIDIFile
from muslang.ast_nodes import *
from muslang.articulations import ArticulationMapper
from muslang.drums import get_drum_midi_note, is_percussion_instrument
from muslang.config import *
from typing import Dict, List, Tuple, Optional


# ============================================================================
# General MIDI Instrument Map
# ============================================================================

INSTRUMENT_MAP = {
    # Piano
    'piano': 0,
    'acoustic_grand_piano': 0,
    'bright_acoustic_piano': 1,
    'electric_grand_piano': 2,
    'honky_tonk_piano': 3,
    'electric_piano_1': 4,
    'electric_piano_2': 5,
    'harpsichord': 6,
    'clavinet': 7,
    
    # Chromatic Percussion
    'celesta': 8,
    'glockenspiel': 9,
    'music_box': 10,
    'vibraphone': 11,
    'marimba': 12,
    'xylophone': 13,
    'tubular_bells': 14,
    'dulcimer': 15,
    
    # Organ
    'organ': 16,
    'drawbar_organ': 16,
    'percussive_organ': 17,
    'rock_organ': 18,
    'church_organ': 19,
    'reed_organ': 20,
    'accordion': 21,
    'harmonica': 22,
    'tango_accordion': 23,
    
    # Guitar
    'guitar': 24,
    'acoustic_guitar_nylon': 24,
    'acoustic_guitar_steel': 25,
    'electric_guitar_jazz': 26,
    'electric_guitar_clean': 27,
    'electric_guitar_muted': 28,
    'overdriven_guitar': 29,
    'distortion_guitar': 30,
    'guitar_harmonics': 31,
    
    # Bass
    'bass': 32,
    'acoustic_bass': 32,
    'electric_bass_finger': 33,
    'electric_bass_pick': 34,
    'fretless_bass': 35,
    'slap_bass_1': 36,
    'slap_bass_2': 37,
    'synth_bass_1': 38,
    'synth_bass_2': 39,
    
    # Strings
    'violin': 40,
    'viola': 41,
    'cello': 42,
    'contrabass': 43,
    'tremolo_strings': 44,
    'pizzicato_strings': 45,
    'orchestral_harp': 46,
    'timpani': 47,
    
    # Ensemble
    'string_ensemble_1': 48,
    'string_ensemble_2': 49,
    'synth_strings_1': 50,
    'synth_strings_2': 51,
    'choir_aahs': 52,
    'voice_oohs': 53,
    'synth_voice': 54,
    'orchestra_hit': 55,
    
    # Brass
    'trumpet': 56,
    'trombone': 57,
    'tuba': 58,
    'muted_trumpet': 59,
    'french_horn': 60,
    'brass_section': 61,
    'synth_brass_1': 62,
    'synth_brass_2': 63,
    
    # Reed
    'soprano_sax': 64,
    'alto_sax': 65,
    'tenor_sax': 66,
    'baritone_sax': 67,
    'oboe': 68,
    'english_horn': 69,
    'bassoon': 70,
    'clarinet': 71,
    
    # Pipe
    'piccolo': 72,
    'flute': 73,
    'recorder': 74,
    'pan_flute': 75,
    'blown_bottle': 76,
    'shakuhachi': 77,
    'whistle': 78,
    'ocarina': 79,
    
    # Synth Lead
    'lead_1_square': 80,
    'lead_2_sawtooth': 81,
    'lead_3_calliope': 82,
    'lead_4_chiff': 83,
    'lead_5_charang': 84,
    'lead_6_voice': 85,
    'lead_7_fifths': 86,
    'lead_8_bass_lead': 87,
    
    # Synth Pad
    'pad_1_new_age': 88,
    'pad_2_warm': 89,
    'pad_3_polysynth': 90,
    'pad_4_choir': 91,
    'pad_5_bowed': 92,
    'pad_6_metallic': 93,
    'pad_7_halo': 94,
    'pad_8_sweep': 95,
    
    # Synth Effects
    'fx_1_rain': 96,
    'fx_2_soundtrack': 97,
    'fx_3_crystal': 98,
    'fx_4_atmosphere': 99,
    'fx_5_brightness': 100,
    'fx_6_goblins': 101,
    'fx_7_echoes': 102,
    'fx_8_sci_fi': 103,
    
    # Ethnic
    'sitar': 104,
    'banjo': 105,
    'shamisen': 106,
    'koto': 107,
    'kalimba': 108,
    'bag_pipe': 109,
    'fiddle': 110,
    'shanai': 111,
    
    # Percussive
    'tinkle_bell': 112,
    'agogo': 113,
    'steel_drums': 114,
    'woodblock': 115,
    'taiko_drum': 116,
    'melodic_tom': 117,
    'synth_drum': 118,
    'reverse_cymbal': 119,
    
    # Sound Effects
    'guitar_fret_noise': 120,
    'breath_noise': 121,
    'seashore': 122,
    'bird_tweet': 123,
    'telephone_ring': 124,
    'helicopter': 125,
    'applause': 126,
    'gunshot': 127,
}


# ============================================================================
# MIDI Generator Class
# ============================================================================

class MIDIGenerator:
    """
    Generate MIDI file from analyzed AST.
    
    This class walks through the AST and generates corresponding MIDI events,
    including notes, control changes, and meta-events. It manages MIDI channels,
    tracks articulation and dynamic state, and handles advanced features like
    slurs, slides, and percussion.
    
    Attributes:
        ppq: Pulses per quarter note (MIDI timing resolution)
        midi: MIDIFile object from midiutil
        channel_counter: Counter for assigning MIDI channels
        instrument_channels: Map of instrument names to MIDI channels
    """
    
    def __init__(self, ppq: int = DEFAULT_MIDI_PPQ):
        """
        Initialize MIDI generator.
        
        Args:
            ppq: Pulses per quarter note (resolution)
        """
        self.ppq = ppq
        self.midi: Optional[MIDIFile] = None
        self.channel_counter = 0
        self.instrument_channels: Dict[str, int] = {}
    
    def generate(self, ast: Sequence, output_path: str):
        """
        Generate MIDI file from AST.
        
        Args:
            ast: Analyzed AST (Sequence node with instruments dict)
            output_path: Path to output MIDI file
        """
        # Get instruments from dict
        if not ast.instruments:
            raise ValueError("No instruments found in composition")
        
        instruments = list(ast.instruments.values())
        num_tracks = len(instruments)
        
        # Create MIDI file
        self.midi = MIDIFile(num_tracks, deinterleave=False)
        
        # Add default tempo (can be overridden by tempo directives)
        self.midi.addTempo(0, 0, DEFAULT_TEMPO)
        
        # Process each instrument
        for track_num, instrument in enumerate(instruments):
            self._process_instrument(track_num, instrument)
        
        # Write MIDI file
        with open(output_path, 'wb') as f:
            self.midi.writeFile(f)
    
    def _process_instrument(self, track_num: int, instrument: Instrument):
        """
        Process an instrument and generate MIDI events.
        
        All notes must be in voices. Directives (tempo, time signature, etc.)
        are at the instrument level and don't advance time.
        
        Args:
            track_num: MIDI track number
            instrument: Instrument AST node
        """
        # Assign MIDI channel
        if is_percussion_instrument(instrument.name):
            channel = GM_DRUM_CHANNEL
        else:
            channel = self._get_next_channel()
            # Set program (instrument sound)
            program = INSTRUMENT_MAP.get(instrument.name.lower(), 0)
            self.midi.addProgramChange(track_num, channel, 0, program)
        
        self.instrument_channels[instrument.name] = channel
        
        # Initialize state
        mapper = ArticulationMapper()
        
        # Process instrument-level directives (tempo, time signature, etc.)
        # These don't advance time, so we can process them all at time 0
        for event in instrument.events:
            self._process_event(track_num, channel, event, 0, mapper)
        
        # Process voices (each voice starts at time 0, plays simultaneously)
        for voice_num, voice_events in instrument.voices.items():
            # Each voice starts at time 0 (simultaneous playback)
            time_ticks = 0
            for event in voice_events:
                time_ticks = self._process_event(
                    track_num, channel, event, time_ticks, mapper
                )
    
    def _process_event(
        self, 
        track: int, 
        channel: int, 
        event: ASTNode, 
        time_ticks: int, 
        mapper: ArticulationMapper
    ) -> int:
        """
        Process a single event and return new time in ticks.
        
        Args:
            track: MIDI track number
            channel: MIDI channel number
            event: AST event node
            time_ticks: Current time in MIDI ticks
            mapper: Articulation/dynamic state tracker
        
        Returns:
            New time in ticks after processing event
        """
        
        if isinstance(event, Note):
            return self._generate_note(track, channel, event, time_ticks, mapper)
        
        elif isinstance(event, Rest):
            # Advance time without generating note
            duration_ticks = self._duration_to_ticks(
                event.duration or DEFAULT_NOTE_DURATION, 
                event.dotted
            )
            return time_ticks + duration_ticks
        
        elif isinstance(event, Chord):
            # Generate all notes at same time
            max_duration = 0
            for note in event.notes:
                self._generate_note(track, channel, note, time_ticks, mapper)
                duration_ticks = self._duration_to_ticks(
                    note.duration or DEFAULT_NOTE_DURATION, 
                    note.dotted
                )
                max_duration = max(max_duration, duration_ticks)
            return time_ticks + max_duration
        
        elif isinstance(event, Articulation):
            mapper.process_articulation(event)
            return time_ticks
        
        elif isinstance(event, DynamicLevel):
            mapper.process_dynamic_level(event.level)
            return time_ticks
        
        elif isinstance(event, DynamicTransition):
            mapper.process_dynamic_transition(event.type)
            return time_ticks
        
        elif isinstance(event, DynamicAccent):
            # Accents are handled per-note, just track for next note
            return time_ticks
        
        elif isinstance(event, Reset):
            mapper.process_reset(event.type)
            return time_ticks
        
        elif isinstance(event, Tempo):
            time_beats = time_ticks / self.ppq
            self.midi.addTempo(track, time_beats, event.bpm)
            return time_ticks
        
        elif isinstance(event, TimeSignature):
            time_beats = time_ticks / self.ppq
            # MIDI time signature: numerator, denominator (as power of 2)
            # Denominator encoding: 2=1 (half), 4=2 (quarter), 8=3 (eighth), 16=4 (sixteenth)
            # midiutil expects the encoded value, not the actual denominator
            import math
            denominator_encoded = int(math.log2(event.denominator))
            self.midi.addTimeSignature(
                track, time_beats, 
                event.numerator, denominator_encoded, 
                24  # MIDI clock ticks per metronome click
            )
            return time_ticks
        
        elif isinstance(event, Pan):
            time_beats = time_ticks / self.ppq
            # Pan: 0=left, 64=center, 127=right
            pan_value = max(0, min(127, event.position))
            self.midi.addControllerEvent(track, channel, time_beats, CC_PAN, pan_value)
            return time_ticks
        
        elif isinstance(event, Slur):
            return self._generate_slur(track, channel, event, time_ticks, mapper)
        
        elif isinstance(event, Slide):
            return self._generate_slide(track, channel, event, time_ticks, mapper)
        
        elif isinstance(event, PercussionNote):
            midi_note = get_drum_midi_note(event.drum_sound)
            duration_ticks = self._duration_to_ticks(
                event.duration or DEFAULT_NOTE_DURATION, 
                event.dotted
            )
            velocity = mapper.get_note_velocity()
            
            time_beats = time_ticks / self.ppq
            duration_beats = duration_ticks / self.ppq
            
            self.midi.addNote(
                track, channel, midi_note,
                time_beats, duration_beats, velocity
            )
            return time_ticks + duration_ticks
        
        elif isinstance(event, Voice):
            # Voice changes are handled at parsing/semantic level
            # The events within voices are flattened into the instrument
            return time_ticks
        
        elif isinstance(event, Sequence):
            # Process nested sequences
            for sub_event in event.events:
                time_ticks = self._process_event(
                    track, channel, sub_event, time_ticks, mapper
                )
            return time_ticks
        
        # Unknown event type - skip
        return time_ticks
    
    def _generate_note(
        self, 
        track: int, 
        channel: int, 
        note: Note, 
        time_ticks: int, 
        mapper: ArticulationMapper,
        overlap: bool = False,
        accent: Optional[str] = None
    ) -> int:
        """
        Generate MIDI note on/off events.
        
        Args:
            track: MIDI track number
            channel: MIDI channel number
            note: Note AST node
            time_ticks: Current time in MIDI ticks
            mapper: Articulation/dynamic state tracker
            overlap: Whether to overlap note with next (for legato)
            accent: Optional accent type (sforzando, forte-piano)
        
        Returns:
            New time in ticks after note
        """
        # Calculate MIDI note number
        midi_note = self._note_to_midi(note)
        
        # Calculate duration
        base_duration_ticks = self._duration_to_ticks(
            note.duration or DEFAULT_NOTE_DURATION, 
            note.dotted
        )
        actual_duration_ticks = mapper.get_note_duration(base_duration_ticks)
        
        # Calculate velocity
        velocity = mapper.get_note_velocity(accent)
        
        # Convert to beats for MIDI
        time_beats = time_ticks / self.ppq
        duration_beats = actual_duration_ticks / self.ppq
        
        # Add note
        self.midi.addNote(
            track, channel, midi_note,
            time_beats, duration_beats, velocity
        )
        
        # Add legato CC if needed
        if mapper.should_add_legato_cc():
            self.midi.addControllerEvent(track, channel, time_beats, CC_LEGATO, 127)
        
        # Advance time
        if overlap:
            # For slurred notes, advance by slightly less than full duration
            return time_ticks + int(actual_duration_ticks * 0.95)
        else:
            # Normal: advance by full base duration
            return time_ticks + base_duration_ticks
    
    def _generate_slur(
        self, 
        track: int, 
        channel: int, 
        slur: Slur, 
        time_ticks: int, 
        mapper: ArticulationMapper
    ) -> int:
        """
        Generate slurred notes with overlap and legato CC.
        
        Args:
            track: MIDI track number
            channel: MIDI channel number
            slur: Slur AST node
            time_ticks: Current time in MIDI ticks
            mapper: Articulation/dynamic state tracker
        
        Returns:
            New time in ticks after slur
        """
        # Enable legato CC at start
        time_beats = time_ticks / self.ppq
        self.midi.addControllerEvent(track, channel, time_beats, CC_LEGATO, 127)
        
        # Generate slurred notes with overlap
        slur_time_ticks = time_ticks
        for i, note in enumerate(slur.notes):
            is_last = (i == len(slur.notes) - 1)
            overlap = not is_last  # Overlap all but last note
            slur_time_ticks = self._generate_note(
                track, channel, note, slur_time_ticks, mapper, overlap=overlap
            )
        
        # Disable legato CC at end
        end_time_beats = slur_time_ticks / self.ppq
        self.midi.addControllerEvent(track, channel, end_time_beats, CC_LEGATO, 0)
        
        return slur_time_ticks
    
    def _generate_slide(
        self, 
        track: int, 
        channel: int, 
        slide: Slide, 
        time_ticks: int, 
        mapper: ArticulationMapper
    ) -> int:
        """
        Generate pitch bend events for slide/glissando.
        
        Args:
            track: MIDI track number
            channel: MIDI channel number
            slide: Slide AST node
            time_ticks: Current time in MIDI ticks
            mapper: Articulation/dynamic state tracker
        
        Returns:
            New time in ticks after slide
        """
        from_midi = self._note_to_midi(slide.from_note)
        to_midi = self._note_to_midi(slide.to_note)
        
        duration_ticks = self._duration_to_ticks(
            slide.from_note.duration or DEFAULT_NOTE_DURATION,
            slide.from_note.dotted
        )
        
        if slide.style == 'chromatic':
            # Generate pitch bend events
            semitones = to_midi - from_midi
            
            # Calculate bend values
            steps = SLIDE_STEPS
            for i in range(steps + 1):
                bend_time_ticks = time_ticks + (duration_ticks * i // steps)
                bend_time_beats = bend_time_ticks / self.ppq
                
                # Calculate pitch bend value
                # Pitch bend is 14-bit: 0-16383, center is 8192
                # Range is typically ±2 semitones
                # MIDIFile.addPitchWheelEvent expects -8192 to +8191 (signed 14-bit)
                bend_value = int((8192 * semitones * i) / (steps * PITCH_BEND_RANGE))
                bend_value = max(-8192, min(8191, bend_value))
                
                self.midi.addPitchWheelEvent(track, channel, bend_time_beats, bend_value)
            
            # Add the note at original pitch
            velocity = mapper.get_note_velocity()
            time_beats = time_ticks / self.ppq
            duration_beats = duration_ticks / self.ppq
            
            self.midi.addNote(
                track, channel, from_midi,
                time_beats, duration_beats, velocity
            )
            
            # Reset pitch bend to center (0 for midiutil's signed format)
            end_time_beats = (time_ticks + duration_ticks) / self.ppq
            self.midi.addPitchWheelEvent(track, channel, end_time_beats, 0)
        
        elif slide.style == 'stepped':
            # Generate intermediate chromatic notes
            step = 1 if to_midi > from_midi else -1
            num_steps = abs(to_midi - from_midi)
            
            if num_steps == 0:
                # Same note - just play once
                return self._generate_note(track, channel, slide.from_note, time_ticks, mapper)
            
            velocity = mapper.get_note_velocity()
            step_duration_ticks = duration_ticks // (num_steps + 1)
            
            current_pitch = from_midi
            current_time_ticks = time_ticks
            
            # Generate intermediate steps
            while current_pitch != to_midi:
                time_beats = current_time_ticks / self.ppq
                duration_beats = step_duration_ticks / self.ppq
                
                self.midi.addNote(
                    track, channel, current_pitch,
                    time_beats, duration_beats, velocity
                )
                
                current_pitch += step
                current_time_ticks += step_duration_ticks
            
            # Final note
            time_beats = current_time_ticks / self.ppq
            duration_beats = step_duration_ticks / self.ppq
            self.midi.addNote(
                track, channel, to_midi,
                time_beats, duration_beats, velocity
            )
        
        elif slide.style == 'portamento':
            # Use portamento CC
            time_beats = time_ticks / self.ppq
            
            # Set portamento time (0-127, higher = slower)
            portamento_time = min(127, duration_ticks // 10)
            self.midi.addControllerEvent(track, channel, time_beats, CC_PORTAMENTO_TIME, portamento_time)
            self.midi.addControllerEvent(track, channel, time_beats, CC_PORTAMENTO_SWITCH, 127)
            
            # Generate from note
            velocity = mapper.get_note_velocity()
            duration_beats = duration_ticks / self.ppq
            
            self.midi.addNote(
                track, channel, from_midi,
                time_beats, duration_beats, velocity
            )
            
            # Disable portamento
            end_time_beats = (time_ticks + duration_ticks) / self.ppq
            self.midi.addControllerEvent(track, channel, end_time_beats, CC_PORTAMENTO_SWITCH, 0)
        
        return time_ticks + duration_ticks
    
    def _note_to_midi(self, note: Note) -> int:
        """
        Convert Note AST node to MIDI note number.
        
        MIDI note numbers: C-1=0, C0=12, C1=24, ..., C4 (middle C)=60, ..., G9=127
        
        Args:
            note: Note AST node
        
        Returns:
            MIDI note number (0-127)
        """
        pitch_map = {
            'c': 0, 'd': 2, 'e': 4, 'f': 5, 
            'g': 7, 'a': 9, 'b': 11
        }
        
        # Base MIDI note number
        midi_note = (note.octave + 1) * 12 + pitch_map[note.pitch]
        
        # Apply accidental
        if note.accidental == 'sharp':
            midi_note += 1
        elif note.accidental == 'flat':
            midi_note -= 1
        # 'natural' accidental doesn't change pitch (cancels key signature)
        
        # Clamp to valid MIDI range
        return max(MIDI_MIN_NOTE, min(MIDI_MAX_NOTE, midi_note))
    
    def _duration_to_ticks(self, duration: int, dotted: bool) -> int:
        """
        Convert note duration to MIDI ticks.
        
        Args:
            duration: Note duration (1=whole, 2=half, 4=quarter, etc.)
            dotted: Whether note is dotted (1.5x duration)
        
        Returns:
            Duration in MIDI ticks
        """
        # Calculate base duration in ticks
        # Whole note = 4 quarter notes = 4 * ppq ticks
        ticks = (4 * self.ppq) // duration
        
        # Apply dotted note multiplier
        if dotted:
            ticks = int(ticks * DOT_MULTIPLIER)
        
        return ticks
    
    def _get_next_channel(self) -> int:
        """
        Get next available MIDI channel.
        
        Returns:
            MIDI channel number (0-15)
        
        Raises:
            ValueError: If no channels available (max 15 non-percussion instruments)
        """
        channel = self.channel_counter
        self.channel_counter += 1
        
        # Skip drum channel (9)
        if channel == GM_DRUM_CHANNEL:
            channel += 1
            self.channel_counter += 1
        
        if channel > MIDI_MAX_CHANNEL:
            raise ValueError("Too many instruments (max 15 non-percussion)")
        
        return channel
