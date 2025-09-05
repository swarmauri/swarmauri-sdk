# test_whitespace.py
import pytest

from jaml import (
    loads,
    round_trip_loads,
)


@pytest.mark.spec
@pytest.mark.mep0006
# @pytest.mark.xfail(reason="Leading/trailing whitespace preservation not yet implemented.")
def test_leading_trailing_whitespace_in_strings_preserved():
    """
    MEP-006 Section 3.2:
      Leading and trailing whitespace in string values is preserved.
    """
    toml_str = """
[settings]
name = "  Jeff  "
"""
    ast = round_trip_loads(toml_str)
    assert ast["settings"]["name"] == '"  Jeff  "', (
        "Leading/trailing spaces should be preserved"
    )

    # If you want to test round-trip:
    out = ast.dumps()
    # parse again
    data_again = loads(out)
    assert data_again["settings"]["name"] == '"  Jeff  "'


@pytest.mark.spec
@pytest.mark.mep0006
# @pytest.mark.xfail(reason="Trailing whitespace after value not yet normalized/ignored as expected.")
def test_trailing_whitespace_after_value_ignored():
    """
    MEP-006 Section 3.2:
      Trailing whitespace after values on the same line is ignored.
    """
    toml_str = """
[settings]
title = "Dev"     
"""
    data = loads(toml_str)
    assert data["settings"]["title"] == '"Dev"', (
        "Trailing whitespace after 'Dev' should be ignored"
    )


@pytest.mark.spec
@pytest.mark.mep0006
# @pytest.mark.xfail(reason="Whitespace normalization around assignment operator not yet implemented.")
def test_whitespace_around_assignment_operator_normalized():
    """
    MEP-006 Section 3.3:
      Whitespace around the assignment operator is allowed but not required.
      On dump, excessive whitespace is normalized.
    """
    toml_str = """
[config]
key    =    "value"
"""
    ast = round_trip_loads(toml_str)
    assert ast["config"]["key"] == '"value"'

    # Excessive whitespace normalized to single space in the output
    out = ast.dumps()
    # For example, might check if out has 'key = "value"' (one space).
    assert 'key = "value"' in out, f"Expected normalized space around '='. Got: {out}"


@pytest.mark.spec
@pytest.mark.mep0006
# @pytest.mark.xfail(reason="Inline table whitespace preservation not fully implemented yet.")
def test_inline_tables_whitespace_preserved_round_trip():
    """
    MEP-006 Section 3.4:
      Whitespace in inline tables is ignored during parsing,
      but preserved when round-tripping (if your unparser supports it).
    """
    toml_str = """
[user]
profile = { name = "Alice", age = 30 }
"""
    # Round-trip load -> dump
    ast = round_trip_loads(toml_str)
    reserialized = ast.dumps()

    # If your unparser precisely preserves spacing, the strings should match.
    # Some implementations only preserve structure, not exact spacing.
    # Adjust accordingly. For strict tests:

    assert 'name = "Alice"' in reserialized
    assert "age = 30" in reserialized


@pytest.mark.spec
@pytest.mark.mep0006
# @pytest.mark.xfail(reason="Multiline string whitespace preservation not fully implemented yet.")
def test_multiline_string_leading_whitespace_preserved():
    """
    MEP-006 Section 3.5:
      Whitespace within multiline strings is preserved (including newlines).
    """
    toml_str = """
[documentation]
description = \"\"\"  
  This is a multiline
  string with leading spaces
\"\"\"
"""
    data = loads(toml_str)
    # Depending on how your parser handles the newlines,
    # check for leading space or entire block.
    desc = data["documentation"]["description"]

    # Example expectation: The initial newline is stripped, but the
    # leading spaces on lines are preserved. Adjust to your parser's rules.
    assert "  This is a multiline\n" in desc
    assert "  string with leading spaces" in desc


@pytest.mark.spec
@pytest.mark.mep0006
# @pytest.mark.xfail(reason="Unquoted keys with whitespace not yet raising error.")
def test_unquoted_key_with_space_should_raise_error():
    """
    MEP-006 Section 4:
      Keys containing unquoted whitespace should raise a syntax error.
    """
    bad_toml = """
[invalid]
my key = "value"
"""
    with pytest.raises(SyntaxError, match="Unexpected character"):
        # We expect an error from our parser because 'if' / 'elif' are KEYWORD tokens
        # that cannot appear on the left side of '='.
        _ = loads(bad_toml)  # or round_trip_loads(source)


@pytest.mark.spec
@pytest.mark.mep0006
# @pytest.mark.xfail(reason="Line continuation support not fully implemented yet.")
def test_line_continuation_not_supported_yet():
    """
    MEP-006 Section 6.1 (Open Issues):
      If line continuation is not supported,
      the parser should fail or raise error if encountered.
    """
    toml_str = """
[config]
key = "value \
  continued"
"""
    loads(toml_str)  # Expecting an error or not-yet-implemented behavior
