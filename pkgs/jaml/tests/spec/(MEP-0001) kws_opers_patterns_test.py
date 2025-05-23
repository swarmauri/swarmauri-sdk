import pytest

from jaml import (
    loads,
)

# Optional: If you want to specifically test error states in the parser,
# you can import JMLParser from jaml.parser for advanced scenarios.


@pytest.mark.spec
@pytest.mark.unit
@pytest.mark.mep0001
def test_reserved_keywords():
    """
    Tests that MEP-001 reserved keywords (e.g., 'if', 'elif', etc.)
    cannot be used as valid identifiers. We expect a SyntaxError
    when we parse 'if = 42'.
    """
    source = "if = 42\nelif = 10\ndata = true"
    with pytest.raises(SyntaxError, match="Unexpected character"):
        # We expect an error from our parser because 'if' / 'elif' are KEYWORD tokens
        # that cannot appear on the left side of '='.
        _ = loads(source)  # or round_trip_loads(source)


@pytest.mark.spec
@pytest.mark.unit
@pytest.mark.mep0001
def test_reserved_functions():
    """
    MEP-001 states that 'File()' and 'Git()' are reserved for special usage.
    Ensure they cannot be used as normal identifiers or misapplied.
    """
    source = "File = 'some file'\nGit = 'some repo'"
    with pytest.raises(SyntaxError, match="Unexpected character"):
        # The parser should refuse to let 'File()' or 'Git()' be used as keys if your grammar forbids it.
        _ = loads(source)


@pytest.mark.spec
@pytest.mark.mep0001
def test_reserved_punctuation():
    """
    Verifies that reserved punctuation (like ':' or '=') cannot be part of unquoted keys.
    e.g. some:key = 1
    """
    source = "some:key = 1"
    with pytest.raises(SyntaxError, match="Unexpected character"):
        _ = loads(source)


@pytest.mark.spec
@pytest.mark.mep0001
def test_trailing_punctuation_allowed():
    """
    Verifies that reserved punctuation (like ':' or '=') is allowed.
    e.g. some: key = 1
    """
    source = "some: int = 1"
    _ = loads(source)


@pytest.mark.spec
@pytest.mark.mep0001
def test_single_quote_string():
    source = "single = 'Hello, World!'"
    data = loads(source)
    # Expect that the value has been unquoted correctly.
    assert data["single"] == "'Hello, World!'"


@pytest.mark.spec
@pytest.mark.mep0001
def test_double_quote_string():
    source = 'single = "Hello, World!"'
    data = loads(source)
    # Expect that the value has been unquoted correctly.
    assert data["single"] == '"Hello, World!"'


@pytest.mark.spec
@pytest.mark.mep0001
def test_triple_single_quote_string():
    # The JML source uses triple-single quotes to enclose a triple-double-quoted string.
    # The inner value should be: """One\nTwo\nThree"""
    source = "triple_single = '''\"\"\"One\nTwo\nThree\"\"\"'''"
    data = loads(source)
    expected = "'''\"\"\"One\nTwo\nThree\"\"\"'''"
    assert data["triple_single"] == expected


@pytest.mark.spec
@pytest.mark.mep0001
def test_triple_double_quote_string():
    # The JML source contains a triple-double quoted string with embedded newlines.
    source = 'triple_double = """Line1\nLine2\nLine3"""'
    data = loads(source)
    expected = '"""Line1\nLine2\nLine3"""'
    assert data["triple_double"] == expected


@pytest.mark.spec
@pytest.mark.mep0001
def test_single_backtick_string():
    # The JML source uses backticks to represent a raw string.
    source = "single_backtick = `C:/Users/Name`"
    data = loads(source)
    expected = "`C:/Users/Name`"
    assert data["single_backtick"] == expected


@pytest.mark.spec
@pytest.mark.mep0001
def test_triple_backtick_string():
    # The JML source uses backticks to represent a raw string.
    source = "triple_backtick = ```C:/Users/Name```"
    data = loads(source)
    expected = "```C:/Users/Name```"
    assert data["triple_backtick"] == expected


@pytest.mark.spec
@pytest.mark.mep0001
@pytest.mark.xfail(
    reason="Debating whether or not to allow non-bracket arithmetic operations."
)
def test_arithmetic_operators():
    """
    Tests arithmetic operators: +, -, *, /, %, **
    Currently just ensures that we parse them without error
    and that the OPERATOR tokens appear in your grammar (if needed).
    """
    source = "value = 2 + 3 * 4 - 5 / 1 % 2 ** 3"
    _ = loads(source)


@pytest.mark.spec
@pytest.mark.mep0001
# @pytest.mark.xfail(reason="Spec not fully implemented – pipeline operator not fully enforced")
def test_pipeline_operator():
    """
    Tests the pipeline operator usage: data | transform | filter
    For now, we parse and expect no error or partial usage.
    If your grammar doesn't support it, raise an error or handle as unrecognized.
    """
    source = "result = <{ data | transform | filter }>"
    with pytest.raises(SyntaxError, match="Unexpected character"):
        # If your grammar doesn't allow '|', we might fail.
        _ = loads(source)


@pytest.mark.spec
@pytest.mark.mep0001
def test_conditional_ternary_operator():
    """
    Tests the inline conditional operator: "Active" if cond else "Inactive"
    If your grammar doesn't allow it, we expect a SyntaxError or partial parse.
    """
    source = 'status = <( "Active" if "Active" else "Inactive" )>'
    _ = loads(source)


@pytest.mark.spec
@pytest.mark.mep0001
def test_membership_operators():
    """
    Tests membership 'in' and 'not in'
    """
    source = 'allowed = <( "admin" in ["admin"] )>'
    _ = loads(source)


@pytest.mark.spec
@pytest.mark.mep0001
# @pytest.mark.xfail(reason="Spec not fully implemented – merge operator not recognized yet.")
def test_merge_operator():
    """
    Verifies reservation of '<<' to merge tables or inline tables.
    """
    source = """
[settings]
merged_config = default << user_override
"""
    with pytest.raises(SyntaxError, match="Unexpected character"):
        _ = loads(source)


@pytest.mark.spec
@pytest.mark.mep0001
def test_invalid_use_of_colon():
    """
    Confirms that using a colon as part of a key name triggers a syntax error.
    """
    source = 'invalid:key = "value"'
    with pytest.raises(SyntaxError, match="Unexpected character"):
        _ = loads(source)


@pytest.mark.spec
@pytest.mark.mep0001
def test_keyword_as_identifier():
    """
    Attempts to use a reserved keyword (e.g. 'if') as a variable name.
    Should cause a syntax error.
    """
    source = 'if = "condition"'
    # This specifically tests something like `if = "condition"`, expecting syntax error
    with pytest.raises(SyntaxError, match="Unexpected character"):
        _ = loads(source)


@pytest.mark.spec
@pytest.mark.mep0001
def test_reserved_function_as_var():
    """
    Verifies reservation of 'File()' or 'Git()' as normal identifiers or variables.
    Should raise an error.
    """
    source = 'File = "somefile"'
    with pytest.raises(SyntaxError, match="Unexpected character"):
        _ = loads(source)


@pytest.mark.spec
@pytest.mark.mep0001
def test_identifier_assigned_identifier():
    """
    Verifies that an identifier cannot be assigned to an identifier.
    Should raise an error.
    """
    source = "identifier = another_identifier"
    with pytest.raises(SyntaxError, match="Unexpected character"):
        _ = loads(source)


@pytest.mark.spec
@pytest.mark.mep0001
def test_underscored_identifier():
    """
    Verifies that an identifier cannot be assigned to an identifier.
    Should raise an error.
    """
    source = 'identifier_1 = "test"'
    _ = loads(source)


@pytest.mark.spec
@pytest.mark.mep0001
def test_unmatched_brackets():
    """
    Expect a syntax error when bracket pairs are mismatched or incomplete.
    In this minimal grammar, the naive parser might not check bracket matching.
    If so, we expect an error.
    """
    source = "[config"
    with pytest.raises(SyntaxError, match="Unexpected end of input"):
        _ = loads(source)


@pytest.mark.spec
@pytest.mark.mep0001
def test_invalid_mismatched_quotes():
    """
    Confirms that mismatched quotes trigger a syntax error.
    """
    source = 'bad = "Missing end quote'
    with pytest.raises(SyntaxError, match="Unexpected character"):
        _ = loads(source)


@pytest.mark.spec
@pytest.mark.mep0001
def test_invalid_enclosed_special_character_identifier():
    """
    Expect a syntax error when an invalid special character is used.
    """
    source = 'mykey!a = "strange_value"'
    with pytest.raises(SyntaxError, match="Unexpected character"):
        _ = loads(source)


@pytest.mark.spec
@pytest.mark.mep0001
def test_invalid_prefix_special_character_identifier():
    """
    Expect a syntax error when an invalid special character is used.
    """
    source = '!mykey = "strange_value"'
    with pytest.raises(SyntaxError, match="Unexpected character"):
        _ = loads(source)


@pytest.mark.spec
@pytest.mark.mep0001
def test_invalid_special_character_identifier():
    """
    Expect a syntax error when an invalid special character is used.
    """
    source = 'mykey! = "strange_value"'
    with pytest.raises(SyntaxError, match="Unexpected character"):
        _ = loads(source)
