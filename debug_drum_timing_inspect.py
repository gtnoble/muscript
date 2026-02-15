#!/usr/bin/env python3
"""Debug script to inspect MIDI timing for drums"""
import mido

print("Inspecting test_drum_timing.mid...")
print("="*60)

mid = mido.MidiFile('test_drum_timing.mid')

for i, track in enumerate(mid.tracks):
    print(f"\nTrack {i}: {track.name}")
    print("-"*60)
    abs_time = 0
    note_on_times = {}  # Track when notes start
    
    for msg in track:
        abs_time += msg.time
        
        if msg.type == 'note_on' and msg.velocity > 0:
            channel = msg.channel
            note = msg.note
            velocity = msg.velocity
            time_in_ticks = abs_time
            time_in_beats = abs_time / mid.ticks_per_beat
            
            # Store note-on time for duration calculation
            key = (channel, note)
            note_on_times[key] = abs_time
            
            # Channel 9 is drums (0-indexed)
            if channel == 9:
                print(f"  Drum ON  {note:3d} @ tick {time_in_ticks:6d} ({time_in_beats:8.3f} beats) vel={velocity:3d}")
            else:
                print(f"  Note ON  {note:3d} @ tick {time_in_ticks:6d} ({time_in_beats:8.3f} beats) vel={velocity:3d} ch={channel}")
                
        elif (msg.type == 'note_off') or (msg.type == 'note_on' and msg.velocity == 0):
            channel = msg.channel
            note = msg.note
            time_in_ticks = abs_time
            time_in_beats = abs_time / mid.ticks_per_beat
            
            # Calculate duration
            key = (channel, note)
            if key in note_on_times:
                start_time = note_on_times[key]
                duration_ticks = abs_time - start_time
                duration_beats = duration_ticks / mid.ticks_per_beat
                
                if channel == 9:
                    print(f"  Drum OFF {note:3d} @ tick {time_in_ticks:6d} ({time_in_beats:8.3f} beats) duration={duration_beats:8.3f} beats")
                else:
                    print(f"  Note OFF {note:3d} @ tick {time_in_ticks:6d} ({time_in_beats:8.3f} beats) duration={duration_beats:8.3f} beats ch={channel}")
                    
                del note_on_times[key]
                
        elif msg.type == 'set_tempo':
            tempo = msg.tempo
            bpm = 60000000 / tempo
            print(f"  Tempo: {bpm:.1f} BPM")
        elif msg.type == 'time_signature':
            print(f"  Time signature: {msg.numerator}/{msg.denominator}")
            
print("\n" + "="*60)
print(f"Ticks per beat (PPQ): {mid.ticks_per_beat}")
