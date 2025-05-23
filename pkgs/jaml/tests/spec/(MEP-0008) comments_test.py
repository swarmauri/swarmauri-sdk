# test_comments.py
import pytest

# Adjust these imports to match your actual API or modules
# where round_trip_loads / round_trip_dumps are defined.
from jaml import loads, round_trip_loads


@pytest.mark.spec
@pytest.mark.mep0008
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
    serialized = ast.dumps()
    # Check that the standalone comment is still present exactly
    assert "# This is a standalone comment at the top of the file" in serialized


@pytest.mark.spec
@pytest.mark.mep0008
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
    serialized = ast.dumps()
    # Check that the inline comment is present on the same line
    assert (
        'greeting = "Hello, World!"  # Inline comment: greeting message' in serialized
    )


@pytest.mark.spec
@pytest.mark.mep0008
# @pytest.mark.xfail(reason="Multiline array comment preservation not yet implemented.")
def test_multiline_array_comments_preserved():
    """
    MEP-008:
      Comments may appear among array elements.
      Ensure they are preserved during round-trip.
    """
    original = """[settings]
colors = [
  "blue"    # Accent color
]"""
    ast = round_trip_loads(original)
    serialized = ast.dumps()
    # Check that each inline comment is preserved for each element
    assert original in serialized
    assert "# Accent color" in serialized


@pytest.mark.spec
@pytest.mark.mep0008
# @pytest.mark.xfail(reason="Multiline array comment preservation not yet implemented.")
def test_multiline_array_comment_out_preserved():
    """
    MEP-008:
      Comments may appear among array elements.
      Ensure they are preserved during round-trip.
    """
    original = """[settings]
colors = [
  # "green"
  "blue"    # Accent color
]"""
    ast = round_trip_loads(original)
    serialized = ast.dumps()
    # Check that each inline comment is preserved for each element
    assert original in serialized
    assert '# "green"' in serialized
    assert "# Accent color" in serialized


@pytest.mark.spec
@pytest.mark.mep0008
# @pytest.mark.xfail(reason="Multiline array comment preservation not yet implemented.")
def test_multiline_array_comment_out_preserved_comma():
    """
    MEP-008:
      Comments may appear among array elements.
      Ensure they are preserved during round-trip.
    """
    original = """[settings]
colors = [
  # "green",
  "blue"    # Accent color
]"""
    ast = round_trip_loads(original)
    serialized = ast.dumps()
    # Check that each inline comment is preserved for each element
    assert original in serialized
    assert '# "green"' in serialized
    assert "# Accent color" in serialized


@pytest.mark.spec
@pytest.mark.mep0008
# @pytest.mark.xfail(reason="Multiline array comment preservation not yet implemented.")
def test_multiline_array_comments_preserved_comma():
    """
    MEP-008:
      Comments may appear among array elements.
      Ensure they are preserved during round-trip.
    """
    original = """[settings]
colors = [
  "red",    # Primary Color
  # "green",
  "blue"    # Accent color
]"""
    ast = round_trip_loads(original)
    serialized = ast.dumps()
    # Check that each inline comment is preserved for each element
    assert original in serialized
    assert "# Primary Color" in serialized
    assert '# "green"' in serialized
    assert "# Accent color" in serialized


@pytest.mark.spec
@pytest.mark.mep0008
# @pytest.mark.xfail(reason="Multiline inline table comment preservation not yet implemented.")
def test_multiline_inline_table_comments_preserved():
    """
    MEP-008:
      Comments in multiline inline tables should also be preserved.
    """
    original = '''[user]
profile = {
  alias = "Bob",
  name = "Alice",               # User's name
  email = "alice@example.com",  # User's email
  bio = """
  Alice is a software engineer.
  She loves coding.
  # This '#' is inside the triple-quoted string, so it's not a comment
  """
}'''
    ast = round_trip_loads(original)
    serialized = ast.dumps()
    # Check that the two inline comments remain
    assert "[user.profile]\nalias" in serialized
    assert """"Alice" # User's name""" in serialized
    assert "# User's name" in serialized
    assert "# User's email" in serialized
    # Also verify the triple-quoted block still contains the # as text
    assert "# This '#' is inside the triple-quoted string" in serialized


@pytest.mark.spec
@pytest.mark.mep0008
# @pytest.mark.xfail(reason="Comments within multiline arrays may not preserve exact spacing/newlines.")
def test_multiline_arrays_with_comments_spacing():
    """
    MEP-008:
      Check if exact spacing/newlines around comments in multiline arrays
      is preserved. Marked xfail until fully implemented.
    """
    original = """[settings]
numbers = [
  1,  # first
  2,  # second
  3   # third
]"""
    ast = round_trip_loads(original)
    serialized = ast.dumps()
    # We expect spacing/newlines around the comments to match the original
    # (though some normalizations may be allowed by spec).
    assert original in serialized
    assert "# first" in serialized
    assert "# second" in serialized
    assert "# third" in serialized


@pytest.mark.spec
@pytest.mark.mep0008
def test_multiline_arrays_comment_out_line():
    original = """[settings]
numbers = [
  1,  # first
  # 2,
  3   # third
]"""
    result = loads(original)
    assert 1 in result["settings"]["numbers"]
    assert 2 not in result["settings"]["numbers"]
    assert 3 in result["settings"]["numbers"]

    ast = round_trip_loads(original)
    serialized = ast.dumps()
    # We expect spacing/newlines around the comments to match the original
    # (though some normalizations may be allowed by spec).
    assert original in serialized
    assert "# first" in serialized
    assert "# 2" in serialized
    assert "# third" in serialized


@pytest.mark.spec
@pytest.mark.mep0008
# @pytest.mark.xfail(reason="Leading/trailing whitespace around comments not fully handled yet.")
def test_whitespace_around_comments():
    """
    MEP-008:
      The spec says we shouldn't remove or alter comments,
      but how about leading/trailing whitespace around them?
      Marked xfail if not yet implemented.
    """
    original = """[demo]
key = "value"  #   note the extra spaces before/after comment"""

    ast = round_trip_loads(original)
    serialized = ast.dumps()
    # If the spec requires preserving that extra whitespace, we can do a direct substring check:
    assert 'key = "value"  #   note the extra spaces before' in serialized
