import pytest
from textwrap import dedent
from cayaml import round_trip_loads
from cayaml.ast_nodes import ScalarNode


@pytest.mark.unit
def test_literal_block():
    yaml_str = dedent("""literal_block: |
      Line one
      Line two
    """)
    doc = round_trip_loads(yaml_str)  # doc is a DocumentNode
    node = doc["literal_block"]
    print("DEBUG:", repr(yaml_str))
    assert isinstance(node, ScalarNode), "Expected a ScalarNode"
    assert node.style == "|", f"Got style={node.style}, expected '|'"
    assert node.lines == ["Line one", "Line two"]


@pytest.mark.unit
def test_folded_block():
    """
    Test loading a folded block scalar (>)
    """
    yaml_str = dedent("""
    folded_block: >
      This is folded
      into one line.
    """)
    doc = round_trip_loads(yaml_str)
    node = doc["folded_block"]
    assert isinstance(node, ScalarNode), "Expected a ScalarNode"
    assert node.style == ">", f"Got style={node.style}, expected '>'"
