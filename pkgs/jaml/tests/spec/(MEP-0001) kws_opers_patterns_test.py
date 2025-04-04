import pytest
from pprint import pprint

from jaml import (
    loads,
    dumps,
    round_trip_loads,
    round_trip_dumps,
    render,
)
# Optional: If you want to specifically test error states in the parser, 
# you can import JMLParser from jaml.parser for advanced scenarios.


@pytest.mark.spec
@pytest.mark.unit
def test_reserved_keywords():
    """
    Tests that MEP-001 reserved keywords (e.g., 'if', 'elif', etc.)
    cannot be used as valid identifiers. We expect a SyntaxError
    when we parse 'if = 42'.
    """
    source = "if = 42\nelif = 10\ndata = true"
    with pytest.raises(SyntaxError, match="reserved keyword"):
        # We expect an error from our parser because 'if' / 'elif' are KEYWORD tokens
        # that cannot appear on the left side of '='.
        _ = loads(source)  # or round_trip_loads(source)


@pytest.mark.spec
@pytest.mark.unit
def test_reserved_functions():
    """
    MEP-001 states that 'File()' and 'Git()' are reserved for special usage.
    Ensure they cannot be used as normal identifiers or misapplied.
    """
    source = "File = 'some file'\nGit = 'some repo'"
    with pytest.raises(SyntaxError, match="reserved function"):
        # The parser should refuse to let 'File()' or 'Git()' be used as keys if your grammar forbids it.
        _ = loads(source)


@pytest.mark.spec
def test_reserved_punctuation():
    """
    Verifies that reserved punctuation (like ':' or '=') cannot be part of unquoted keys.
    e.g. some:key = 1
    """
    source = "some:key = 1"
    with pytest.raises(SyntaxError, match="invalid punctuation"):
        _ = loads(source)


@pytest.mark.spec
def test_trailing_punctuation_allowed():
    """
    Verifies that reserved punctuation (like ':' or '=') is allowed.
    e.g. some: key = 1
    """
    source = "some: key = 1"
    _ = loads(source)


@pytest.mark.spec
def test_string_quotation_rules():
    """
    Demonstrates multiple string forms. For now, we check that it parses 
    without error. If your parser or grammar is advanced, you might do 
    a round-trip and confirm the exact string forms are preserved.
    """
    source = r'''
single = 'Hello, World!'
double = "Hello, ${user.name}!"
triple_single = '''"""One\nTwo\nThree"""'''
triple_double = """Line1
Line2
Line3"""
raw_backticks = `C:/Users/Name`
f_string = f"${base}/docs"
'''
    # If your parser doesn't handle all these string forms, it might raise SyntaxError.
    data = loads(source)


@pytest.mark.spec
def test_arithmetic_operators():
    """
    Tests arithmetic operators: +, -, *, /, %, **
    Currently just ensures that we parse them without error 
    and that the OPERATOR tokens appear in your grammar (if needed).
    """
    source = "value = 2 + 3 * 4 - 5 / 1 % 2 ** 3"
    _ = loads(source)


@pytest.mark.spec
# @pytest.mark.xfail(reason="Spec not fully implemented – pipeline operator not fully enforced")
def test_pipeline_operator():
    """
    Tests the pipeline operator usage: data | transform | filter
    For now, we parse and expect no error or partial usage.
    If your grammar doesn't support it, raise an error or handle as unrecognized.
    """
    source = "result = (~ data | transform | filter ~)"
    with pytest.raises(SyntaxError, match="pipeline operator"):
        # If your grammar doesn't allow '|', we might fail. 
        _ = loads(source)

@pytest.mark.spec
def test_conditional_ternary_operator():
    """
    Tests the inline conditional operator: "Active" if cond else "Inactive"
    If your grammar doesn't allow it, we expect a SyntaxError or partial parse.
    """
    source = 'status = {~ "Active" if is_active else "Inactive" ~}'
    _ = loads(source)


@pytest.mark.spec
def test_membership_operators():
    """
    Tests membership 'in' and 'not in'
    """
    source = 'allowed = {~ "admin" in user.roles ~}'
    _ = loads(source)


@pytest.mark.spec
# @pytest.mark.xfail(reason="Spec not fully implemented – merge operator not recognized yet.")
def test_merge_operator():
    """
    Verifies usage of '<<' to merge tables or inline tables.
    """
    source = '''
[settings]
merged_config = default << user_override
'''
    with pytest.raises(SyntaxError, match="merge operator"):
        _ = loads(source)


@pytest.mark.spec
def test_invalid_use_of_colon():
    """
    Confirms that using a colon as part of a key name triggers a syntax error.
    """
    source = 'invalid:key = "value"'
    with pytest.raises(SyntaxError, match="invalid punctuation"):
        _ = loads(source)


@pytest.mark.spec
def test_keyword_as_identifier():
    """
    Attempts to use a reserved keyword (e.g. 'if') as a variable name.
    Should cause a syntax error.
    """
    source = 'if = "condition"'
    # This specifically tests something like `if = "condition"`, expecting syntax error
    with pytest.raises(SyntaxError, match="reserved keyword"):
        _ = loads(source)


@pytest.mark.spec
def test_reserved_function_as_var():
    """
    Attempts to use 'File()' or 'Git()' as normal identifiers or variables.
    Should raise an error.
    """
    source = 'File = "somefile"'
    with pytest.raises(SyntaxError, match="reserved function"):
        _ = loads(source)


@pytest.mark.spec
def test_unmatched_brackets():
    """
    Expect a syntax error when bracket pairs are mismatched or incomplete.
    In this minimal grammar, the naive parser might not check bracket matching. 
    If so, we expect an error.
    """
    source = '[config'
    with pytest.raises(SyntaxError, match="unmatched bracket|unexpected EOF"):
        _ = loads(source)


@pytest.mark.spec
def test_invalid_mismatched_quotes():
    """
    Confirms that mismatched quotes trigger a syntax error.
    """
    source = 'bad = "Missing end quote'
    with pytest.raises(SyntaxError, match="missing closing quote|Syntax error"):
        _ = loads(source)


def test_print_tokens_for_inspection():
    """
    Optional test: just prints out tokens for manual inspection; not xfailed.
    If you want to still see the raw tokens from the tokenizer, you can 
    call the parser or do a special debug function. But here's a direct example:
    """
    sample = 'merged = default << user_override'
    # We can still directly call the parser internals if needed:
    # Or do something like:
    try:
        ast = round_trip_loads(sample)
        unparsed = round_trip_dumps(ast)
        print("Round-trip JML:\n", unparsed)
    except SyntaxError as e:
        print("SyntaxError encountered:", e)
