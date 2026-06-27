from cayaml import round_trip_loads, dumps


def test_inline_comment_preservation():
    """
    Tests that inline comments are preserved or do not cause parse errors.
    Depending on the library, they may be stored or ignored.
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
    # or re-dumping with the same comments.
    # That usually requires a more advanced YAML parser.
    output = dumps(data)
    # For demonstration, let's say we'd want the comments back:
    assert "# This is an inline comment" in output
    assert "# Another comment" in output
