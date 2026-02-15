#!/usr/bin/env python3
"""Debug script to check voice parsing"""

from muslang.parser import parse_muslang
from muslang.semantics import SemanticAnalyzer

source = """
piano:
  V1: c4/4 d4/4
  V2: e3/2
"""

ast = parse_muslang(source)
print("Parsed AST:")
print(f"Instruments: {list(ast.instruments.keys())}")
inst = ast.instruments['piano']
print(f"Piano events: {len(inst.events)}")
print(f"Piano voices: {list(inst.voices.keys())}")
for i, event in enumerate(inst.events):
    print(f"  {i}: {type(event).__name__} - {event}")

analyzer = SemanticAnalyzer()
result = analyzer.analyze(ast)

inst_result = result.instruments['piano']
print(f"\nAfter semantic analysis:")
print(f"Piano events: {len(inst_result.events)}")
print(f"Piano voices: {list(inst_result.voices.keys())}")
for i, event in enumerate(inst_result.events):
    print(f"  Event {i}: {type(event).__name__}")
for voice_num, events in inst_result.voices.items():
    print(f"  Voice {voice_num}: {len(events)} events")
    for i, event in enumerate(events):
        print(f"    {i}: {type(event).__name__}")
