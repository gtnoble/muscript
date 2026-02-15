#!/usr/bin/env python3
"""Debug script to inspect voice processing."""

from muslang.parser import parse_muslang
from muslang.semantics import SemanticAnalyzer
from muslang.midi_gen import MIDIGenerator

# Simple multi-voice drum pattern
test_input = """
drums: [
  V1: kick/4 kick/4
  V2: snare/4 snare/4
  V3: hat/4 hat/4
] * 2
"""

print("=" * 80)
print("PARSING")
print("=" * 80)

ast = parse_muslang(test_input)

print("\nParsed AST:")
print(f"Instruments: {list(ast.instruments.keys())}")

drums_inst = ast.instruments['drums']
print(f"\nDrums instrument:")
print(f"  Non-voice events: {len(drums_inst.events)}")
print(f"  Voices: {list(drums_inst.voices.keys())}")

for voice_num, voice_events in drums_inst.voices.items():
    print(f"\n  Voice {voice_num}: {len(voice_events)} events")
    for i, event in enumerate(voice_events):
        print(f"    {i}: {event}")

print("\n" + "=" * 80)
print("SEMANTIC ANALYSIS")
print("=" * 80)

analyzer = SemanticAnalyzer()
analyzed_ast = analyzer.analyze(ast)

drums_inst = analyzed_ast.instruments['drums']
print(f"\nAfter semantic analysis:")
print(f"  Non-voice events: {len(drums_inst.events)}")
print(f"  Voices: {list(drums_inst.voices.keys())}")

for voice_num, voice_events in drums_inst.voices.items():
    print(f"\n  Voice {voice_num}: {len(voice_events)} events")
    for i, event in enumerate(voice_events[:10]):  # Limit to first 10
        print(f"    {i}: {event}")
    if len(voice_events) > 10:
        print(f"    ... and {len(voice_events) - 10} more")

print("\n" + "=" * 80)
print("MIDI GENERATION")
print("=" * 80)

generator = MIDIGenerator()
output_path = "/home/gtnoble/Documents/Projects/muslang/debug_voices.mid"
generator.generate(analyzed_ast, output_path)

print(f"\nMIDI file generated: {output_path}")
print("\nMIDI file info:")
print(f"  PPQ: {generator.ppq}")
print(f"  Instrument channels: {generator.instrument_channels}")
