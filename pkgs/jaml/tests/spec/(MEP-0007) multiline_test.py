# test_multiline.py
import pytest

# Adjust these imports to match your actual API or modules
from jaml import (
    round_trip_loads,
)


@pytest.mark.spec
@pytest.mark.mep0007
# @pytest.mark.xfail(reason="Multiline string preservation not fully implemented yet.")
def test_multiline_string_preserves_format():
    """
    MEP-007 Section 3.1:
      Multiline strings enclosed in triple quotes should preserve
      all newlines and indentation during round-trip.
    """
    toml_str = '''[metadata]
description = """
  This is a multiline
  string that preserves
  all newlines and indentation.
"""'''
    # Round-trip load -> dump
    ast = round_trip_loads(toml_str)
    reserialized = ast.dumps()

    # Check that the multiline block is still present with indentation/newlines
    assert toml_str == reserialized
    # assert '"""' in reserialized
    # assert "  This is a multiline\n" in reserialized
    # assert "string that preserves\n" in reserialized


@pytest.mark.spec
@pytest.mark.mep0007
# @pytest.mark.xfail(reason="Multiline array preservation not fully implemented yet.")
def test_multiline_array_preserves_format():
    """
    MEP-007 Section 3.2:
      Arrays can be multiline. The order of elements and
      intentional line breaks should be preserved.
    """
    toml_str = """[settings]
colors = [
  "red",
  "green",
  "blue"
]"""
    ast = round_trip_loads(toml_str)
    reserialized = ast.dumps()
    # reserialized = round_trip_dumps(ast) # old

    # Check that the array is split across multiple lines
    # and in the same order
    assert toml_str == reserialized


@pytest.mark.spec
@pytest.mark.mep0007
# @pytest.mark.xfail(reason="Multiline inline table formatting not fully implemented yet.")
def test_multiline_inline_table_preserves_format():
    """
    MEP-007 Section 3.3:
      Inline tables can be written across multiple lines.
      Formatting (newlines, indentation) is preserved.
    """
    toml_str = """[user]
profile = {
  name = "Alice",
  email = "alice@example.com",
  bio = \"\"\" 
  Alice is a software engineer.
  with 10 years of experience.
  \"\"\" 
}"""
    ast = round_trip_loads(toml_str)
    reserialized = ast.dumps()
    # reserialized = round_trip_dumps(ast) # old

    # Check that the inline table remains multiline
    assert (
        '[user.profile]\nname = "Alice"\nemail = "alice@example.com"\n' in reserialized
    )
    assert "alice@example.com" in reserialized
    # Ensure the multiline string is still triple-quoted
    assert '"""' in reserialized


@pytest.mark.spec
@pytest.mark.mep0007
# @pytest.mark.xfail(reason="Conversion of inline table to table is not yet supported.")
def test_conversion_of_inline_table_to_section():
    """
    MEP-007 Section 3.3:
      Inline tables can be written across multiple lines.
      Formatting (newlines, indentation) is preserved.
    """
    toml_str = """[user]
profile = {
  name = "Alice",
  email = "alice@example.com",
  bio = \"\"\" 
  Alice is a software engineer.
  with 10 years of experience.
  \"\"\" 
}"""
    ast = round_trip_loads(toml_str)
    reserialized = ast.dumps()
    # reserialized = round_trip_dumps(ast) # old

    # Check that the inline table remains multiline
    assert "[user.profile]" in reserialized


@pytest.mark.spec
@pytest.mark.mep0007
# @pytest.mark.xfail(reason="List of inline tables preservation not fully implemented yet.")
def test_list_of_inline_tables_preserves_structure():
    """
    MEP-007 Section 3.4:
      Lists of inline tables are defined by placing inline tables
      in an array. The structure and newlines must be preserved.
    """
    toml_str = """[project]
name = "jaml"
authors = [
  { name = "Jacob", email = "jacob@swarmauri.com" },
  { name = "Stewart", email = "stewart@swarmauri.com" }
]"""
    ast = round_trip_loads(toml_str)
    reserialized = ast.dumps()
    # reserialized = round_trip_dumps(ast) # old

    # Ensure array of inline tables remains multiline
    # and the key-values remain intact
    assert toml_str == reserialized


@pytest.mark.spec
@pytest.mark.mep0007
# @pytest.mark.xfail(reason="Whitespace handling in multiline strings not finalized.")
def test_whitespace_handling_in_multiline_strings():
    """
    MEP-007 Open Issue:
      Decide how to handle leading and trailing whitespace
      in each line. Currently we expect exact preservation, but
      this test is marked xfail until confirmed/implemented.
    """
    toml_str = r'''[multiline]
notes = """
    Indented line
        Further indentation
"""'''
    ast = round_trip_loads(toml_str)
    reserialized = ast.dumps()
    # reserialized = round_trip_dumps(ast) # old
    # Expect exact indentation preservation, e.g. 4 spaces, then 8 spaces, etc.
    assert "    Indented line\n" in reserialized
    assert "        Further indentation" in reserialized


@pytest.mark.spec
@pytest.mark.mep0007
# @pytest.mark.xfail(reason="Indentation rules for nested inline tables not fully enforced yet.")
def test_indentation_in_multiline_inline_tables():
    """
    MEP-007 Open Issue:
      Clarify indentation within multiline inline tables,
      especially when nested. Currently xfail until
      we finalize the desired approach.
    """
    toml_str = """[deep]
nested = {
    meta = {
        level = 2
    },
    debug = true
}"""
    ast = round_trip_loads(toml_str)
    reserialized = ast.dumps()
    # reserialized = round_trip_dumps(ast) # old
    # We expect to preserve indentation, though the exact approach
    # is not fully implemented yet. This test is xfail.
    assert (
        "[deep.nested]\ndebug = true\n\n[deep.nested.meta]\nlevel = 2" in reserialized
    )
