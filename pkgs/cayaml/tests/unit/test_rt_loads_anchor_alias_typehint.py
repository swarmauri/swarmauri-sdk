import pytest
from cayaml import round_trip_loads


@pytest.mark.xfail(reason="Alias, anchor, and type hint not yet supported by cayaml.")
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
    data = round_trip_loads(yaml_str)
    assert data["mystring"] == "hello"
    assert data["another"] == "hello"
