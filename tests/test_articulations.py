"""
Tests for articulation parsing including the new :natural articulation.
"""
from muslang.parser import parse_muslang
from muslang.ast_nodes import Articulation


def test_natural_articulation_parsing():
    source = """
    piano {
      V1: :natural c4/4 d4/4;
    }
    """
    ast = parse_muslang(source)

    measures = ast.instruments['piano'].voices[1]
    events = [evt for measure in measures for evt in measure.events]

    assert len(events) >= 1
    assert isinstance(events[0], Articulation)
    assert events[0].type == 'natural'
