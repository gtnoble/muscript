#!/usr/bin/env python3
"""Debug script to investigate voice structure after parsing and analysis"""

from muslang.parser import parse_muslang
from muslang.semantics import SemanticAnalyzer

source = """
piano:
  V1: c4/4 d4/4
  V2: e3/2
"""

print("=" * 60)
print("AFTER PARSING:")
print("=" * 60)
ast = parse_muslang(source)
inst = ast.instruments['piano']
print(f"Instrument: {inst.name}")
print(f"Events: {inst.events}")
print(f"Voices dict: {inst.voices}")
print(f"Voices keys: {list(inst.voices.keys())}")
for voice_num, events in inst.voices.items():
    print(f"  Voice {voice_num}: {events}")

print("\n" + "=" * 60)
print("AFTER ANALYSIS:")
print("=" * 60)
analyzer = SemanticAnalyzer()
result = analyzer.analyze(ast)
inst = result.instruments['piano']
print(f"Instrument: {inst.name}")
print(f"Events: {inst.events}")
print(f"Voices dict: {inst.voices}")
print(f"Voices keys: {list(inst.voices.keys())}")
for voice_num, events in inst.voices.items():
    print(f"  Voice {voice_num}: {events}")
