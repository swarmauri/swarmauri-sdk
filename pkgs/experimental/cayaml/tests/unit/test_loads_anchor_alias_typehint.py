from cayaml import loads


def test_anchor_alias_typehint():
    """
    Tests YAML anchor (&) and alias (*) along with an optional type hint (e.g., !!str).
    Example:

        mystring: &s !!str "hello"
        another: *s
    """
    yaml_str = """
    mystring: &s !!str "hello"
    another: *s
    """
    data = loads(yaml_str)
    assert data["mystring"] == "hello"
    assert data["another"] == "hello"
