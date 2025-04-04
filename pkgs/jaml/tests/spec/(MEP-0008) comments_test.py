# test_comments.py
import pytest

# Adjust these imports to match your actual API or modules
# where round_trip_loads / round_trip_dumps are defined.
from jaml import (
    loads,
    round_trip_loads,
    round_trip_dumps
)

@pytest.mark.spec
# @pytest.mark.xfail(reason="Standalone comment preservation not yet implemented.")
def test_standalone_comment_preserved():
    """
    MEP-008:
      Single-line comment at the top or anywhere should be preserved 
      after a round-trip operation.
    """
    original = """
# This is a standalone comment at the top of the file

[section]
key = "value"
"""
    ast = round_trip_loads(original)
    reserialized = round_trip_dumps(ast)
    # Check that the standalone comment is still present exactly
    assert "# This is a standalone comment at the top of the file" in reserialized


@pytest.mark.spec
# @pytest.mark.xfail(reason="Inline comment preservation not yet implemented.")
def test_inline_comment_preserved():
    """
    MEP-008:
      Inline comments after a key-value pair must be preserved 
      in the same line after round-trip.
    """
    original = """
[section]
greeting = "Hello, World!"  # Inline comment: greeting message
"""
    ast = round_trip_loads(original)
    reserialized = round_trip_dumps(ast)
    # Check that the inline comment is present on the same line
    assert '# Inline comment: greeting message' in reserialized


@pytest.mark.spec
# @pytest.mark.xfail(reason="Multiline array comment preservation not yet implemented.")
def test_multiline_array_comments_preserved():
    """
    MEP-008:
      Comments may appear among array elements. 
      Ensure they are preserved during round-trip.
    """
    original = """
[settings]
colors = [
  "red",    # Primary color
  "green",  # Secondary color
  "blue"    # Accent color
]
"""
    ast = round_trip_loads(original)
    reserialized = round_trip_dumps(ast)
    # Check that each inline comment is preserved for each element
    assert "# Primary color" in reserialized
    assert "# Secondary color" in reserialized
    assert "# Accent color" in reserialized


@pytest.mark.spec
# @pytest.mark.xfail(reason="Multiline inline table comment preservation not yet implemented.")
def test_multiline_inline_table_comments_preserved():
    """
    MEP-008:
      Comments in multiline inline tables should also be preserved.
    """
    original = '''
[user]
profile = {
  name = "Alice",               # User's name
  email = "alice@example.com",  # User's email
  bio = """
  Alice is a software engineer.
  She loves coding.
  # This '#' is inside the triple-quoted string, so it's not a comment
  """
}
'''
    ast = round_trip_loads(original)
    reserialized = round_trip_dumps(ast)
    # Check that the two inline comments remain 
    assert "# User's name" in reserialized
    assert "# User's email" in reserialized
    # Also verify the triple-quoted block still contains the # as text
    assert "# This '#' is inside the triple-quoted string" in reserialized


@pytest.mark.spec
# @pytest.mark.xfail(reason="Comments within multiline arrays may not preserve exact spacing/newlines.")
def test_multiline_arrays_with_comments_spacing():
    """
    MEP-008:
      Check if exact spacing/newlines around comments in multiline arrays 
      is preserved. Marked xfail until fully implemented.
    """
    original = """\
[settings]
numbers = [
  1,  # first
  2,  # second
  3   # third
]
"""
    ast = round_trip_loads(original)
    reserialized = round_trip_dumps(ast)
    # We expect spacing/newlines around the comments to match the original 
    # (though some normalizations may be allowed by spec).
    assert "# first" in reserialized
    assert "# second" in reserialized
    assert "# third" in reserialized


@pytest.mark.spec
def test_multiline_arrays_comment_out_line():
    original = """\
[settings]
numbers = [
  1,  # first
  # 2,  
  3   # third
]
"""
    result = loads(original)
    assert 1 in result["settings"]["numbers"]
    assert 2 not in result["settings"]["numbers"]
    assert 3 in result["settings"]["numbers"]

    ast = round_trip_loads(original)
    reserialized = round_trip_dumps(ast)
    # We expect spacing/newlines around the comments to match the original 
    # (though some normalizations may be allowed by spec).
    assert "# first" in reserialized
    assert "# 2" in reserialized
    assert "# third" in reserialized


@pytest.mark.spec
# @pytest.mark.xfail(reason="Leading/trailing whitespace around comments not fully handled yet.")
def test_whitespace_around_comments():
    """
    MEP-008:
      The spec says we shouldn't remove or alter comments, 
      but how about leading/trailing whitespace around them?
      Marked xfail if not yet implemented.
    """
    original = """
[demo]
key = "value"   #   note the extra spaces before/after comment
"""
    ast = round_trip_loads(original)
    reserialized = round_trip_dumps(ast)
    # If the spec requires preserving that extra whitespace, we can do a direct substring check:
    assert 'key = "value"   #   note the extra spaces' in reserialized
