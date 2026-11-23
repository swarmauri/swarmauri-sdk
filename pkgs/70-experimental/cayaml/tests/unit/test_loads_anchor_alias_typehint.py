from cayaml import loads


def test_anchor_alias_typehint():
    """
    Tests YAML anchor, alias, and optional type hint support.
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
