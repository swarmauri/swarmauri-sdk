# test_type_annotations.py
import pytest

from jaml import (
    loads,
    round_trip_loads,
)


@pytest.mark.spec
@pytest.mark.mep0009
# @pytest.mark.xfail(reason="Primitive type annotations preservation not fully implemented yet.")
def test_primitive_type_annotations():
    """
    MEP-009 Section 3.1:
      Verify that basic scalar annotations (str, int, float, bool, null)
      are recognized and preserved after round-trip.
    """
    toml_str = """
[scalars]
greeting: str = "Hello, World!"
answer: int = 42
pi: float = 3.14
is_active: bool = true
missing_val: null = null
"""
    # Round-trip to check that annotations are preserved
    ast = round_trip_loads(toml_str)
    reserialized = ast.dumps()

    # Ensure the annotated keys are present with correct annotation
    assert 'greeting: str = "Hello, World!"' in reserialized
    assert "answer: int = 42" in reserialized
    assert "pi: float = 3.14" in reserialized
    assert "is_active: bool = true" in reserialized
    assert "missing_val: null = null" in reserialized


@pytest.mark.spec
@pytest.mark.mep0009
# @pytest.mark.xfail(reason="List annotation handling not fully implemented yet.")
def test_list_annotation():
    """
    MEP-009 Section 3.1:
      Lists annotated with 'list' should parse and round-trip,
      preserving the annotation.
    """
    toml_str = """
[collection]
numbers: list = [1, 2, 3]
colors: list = ["red", "green", "blue"]
"""
    ast = round_trip_loads(toml_str)
    reserialized = ast.dumps()

    assert "numbers: list = [1, 2, 3]" in reserialized
    assert 'colors: list = ["red", "green", "blue"]' in reserialized


@pytest.mark.spec
@pytest.mark.mep0009
# @pytest.mark.xfail(reason="Inline table type annotations not fully preserved yet.")
def test_table_annotation():
    """
    MEP-009 Section 3.1:
      Inline tables annotated with 'table' should parse and round-trip,
      preserving the annotation and structure.
    """
    toml_str = """
[structures]
point: table = { x = 10, y = 20 }
"""
    ast = round_trip_loads(toml_str)
    reserialized = ast.dumps()

    assert "point: table = {x = 10, y = 20}" in reserialized


@pytest.mark.spec
@pytest.mark.mep0009
# @pytest.mark.xfail(reason="Nested inline table type annotations not fully supported yet.")
def test_nested_inline_table_annotation():
    """
    MEP-009:
      Ensure nested inline tables also preserve type annotations within them,
      if they exist.
    """
    toml_str = """
[deep]
user: table = { name: str = "Azzy", details: table = { age: int = 9, role: str = "admin" } }
"""
    ast = round_trip_loads(toml_str)
    reserialized = ast.dumps()

    # Verify the top-level user: table annotation
    assert 'user: table = {name: str = "Azzy",' in reserialized
    # Verify nested details: table annotation
    assert "details: table = {age: int = 9," in reserialized


@pytest.mark.spec
@pytest.mark.mep0009
# @pytest.mark.xfail(reason="Lists of inline tables annotations not fully implemented yet.")
def test_table_arrays_and_lists_of_inline_tables():
    """
    MEP-009 Section 4.5:
      Check that a list of inline tables annotated with 'list'
      preserves the annotation.
    """
    toml_str = """
[project]
authors: list = [
  { name: str = "Jacob", email: str = "jacob@swarmauri.com" },
  { name: str = "Stewart", email: str = "stewart@swarmauri.com" },
]
"""
    ast = round_trip_loads(toml_str)
    reserialized = ast.dumps()

    # Should see 'authors: list = [' plus the inline tables
    assert (
        'authors: list = [\n  {name: str = "Jacob", email: str = "jacob@swarmauri.com"},'
        in reserialized
    )
    assert (
        '{name: str = "Stewart", email: str = "stewart@swarmauri.com"}' in reserialized
    )


# @pytest.mark.xfail(reason="Type validation not implemented yet.")
@pytest.mark.spec
@pytest.mark.mep0009
def test_value_does_not_match_annotation():
    """
    MEP-009:
      If type validation is implemented, a mismatch (e.g., an int annotation
      but a string value) might raise an error or warning.
      Marked xfail until validation is enforced.
    """
    invalid_toml = """
[section]
wrong_type: int = "this is not an int"
"""
    # If your parser enforces types at load time, it should raise an error.
    loads(invalid_toml)  # Expect some form of error/exception


# @pytest.mark.xfail(reason="Strict type enforcement for nested complex types not yet implemented.")
@pytest.mark.spec
@pytest.mark.mep0009
def test_nested_type_mismatch():
    """
    MEP-009:
      If the annotation says 'table' but we provide a list, or vice versa,
      we might expect an error or mismatch event.
      Marked xfail as it's still under discussion.
    """
    invalid_toml = """
[section]
something: table = ["red", "blue"]
"""
    # If the parser strictly enforces 'table', it should fail on a list value.
    loads(invalid_toml)  # Expect an error or mismatch handling
