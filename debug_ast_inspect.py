#!/usr/bin/env python3
"""Debug script to inspect parsed AST for drum notes"""

from pathlib import Path
from muslang.parser import parse_muslang_file
from muslang.semantics import SemanticAnalyzer
from muslang.ast_nodes import PercussionNote, Instrument

# Parse the test file
tree = parse_muslang_file(Path('test_drum_timing.mus'))
print("Raw parsed tree:")
print(tree)
print("\n" + "="*60 + "\n")

# Run semantic analysis
analyzer = SemanticAnalyzer()
analyzed = analyzer.analyze(tree)

# Find the drums instrument
for name, inst in analyzed.instruments.items():
    if name == 'drums':
        print(f"Instrument: {name}")
        print(f"Events: {len(inst.events)}")
        print(f"Voices: {list(inst.voices.keys())}")
        print("\nNon-voice events:")
        for i, event in enumerate(inst.events):
            if isinstance(event, PercussionNote):
                print(f"  {i}: PercussionNote({event.drum_sound}, duration={event.duration}, dotted={event.dotted}, start={event.start_time}, end={event.end_time})")
            else:
                print(f"  {i}: {type(event).__name__}")
        
        print("\nVoice events:")
        for voice_num, events in inst.voices.items():
            print(f"  Voice {voice_num}:")
            for i, event in enumerate(events):
                if isinstance(event, PercussionNote):
                    print(f"    {i}: PercussionNote({event.drum_sound}, duration={event.duration}, dotted={event.dotted}, start={event.start_time}, end={event.end_time})")
                else:
                    print(f"    {i}: {type(event).__name__}")
