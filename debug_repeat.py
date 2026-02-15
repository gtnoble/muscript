"""Quick debug script to check repeat parsing and expansion"""

from muslang.parser import parse_muslang
from muslang.semantics import SemanticAnalyzer

source = """
piano: [c4/4 d4/4 e4/4] * 3
"""

# Parse
ast = parse_muslang(source)

print("Parsed AST:")
print(f"Type: {type(ast)}")
print(f"Number of top-level events: {len(ast.events)}")

if ast.events:
    instrument = ast.events[0]
    print(f"\nInstrument name: {instrument.name}")
    print(f"Number of instrument events: {len(instrument.events)}")
    for i, event in enumerate(instrument.events):
        print(f"  Event {i}: {type(event).__name__}")
        if hasattr(event, 'sequence'):
            print(f"    Repeat with {len(event.sequence)} items, count={event.count}")
        elif hasattr(event, 'pitch'):
            print(f"    Note: {event.pitch}{event.octave}/{event.duration}")

# Now analyze
analyzer = SemanticAnalyzer()

# Test just the repeat expansion phase
print("\n--- Testing repeat expansion ---")
ast_after_repeat = analyzer._expand_repeats(ast)

print(f"\nAfter repeat expansion:")
if ast_after_repeat.events:
    instrument = ast_after_repeat.events[0]
    print(f"Number of instrument events: {len(instrument.events)}")
    notes = [e for e in instrument.events if hasattr(e, 'pitch')]
    print(f"Number of notes: {len(notes)}")
    for i, event in enumerate(instrument.events[:15]):  # Show first 15
        if hasattr(event, 'pitch'):
            print(f"  Event {i}: Note {event.pitch}{event.octave}/{event.duration}")
        else:
            print(f"  Event {i}: {type(event).__name__}")
