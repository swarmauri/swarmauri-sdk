import pytest
from cayaml import round_trip_loads, dumps


@pytest.mark.xfail(reason="Inline comment preservation not yet supported by cayaml.")
def test_inline_comment_preservation():
    """
    Tests that inline comments (# ...) are preserved (or at least not cause parse errors).
    Depending on the library, we might store them in metadata or simply ignore them.
    """
    yaml_str = """
    key1: value1  # This is an inline comment
    key2: value2 # Another comment
    """
    data = round_trip_loads(yaml_str)
    # Minimally we check that the parser didn't choke on comments
    assert data["key1"] == "value1"
    assert data["key2"] == "value2"

    # If we want comment "preservation", we'd expect them in a data structure,
    # or re-dumping with the same comments. That usually requires a more advanced YAML parser.
    output = dumps(data)
    # For demonstration, let's say we'd want the comments back:
    assert "# This is an inline comment" in output
    assert "# Another comment" in output
