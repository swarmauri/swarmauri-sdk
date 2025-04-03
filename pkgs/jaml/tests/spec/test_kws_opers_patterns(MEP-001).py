import pytest
from pprint import pprint

from jaml._tokenizer import tokenize

@pytest.mark.spec
@pytest.mark.unit
def test_reserved_keywords():
    """
    Tests that MEP-001 reserved keywords (e.g. 'if', 'elif', 'true', etc.)
    are recognized correctly and cannot be used as valid identifiers.
    """
    source = "if = 42\nelif = 10\ndata = true"
    # Expect: syntax error or tokens that show the misuse of 'if' and 'elif'.
    try:
        tokens = tokenize(source)
        # If we do get tokens, let's see if any produce an error for usage as identifiers.
        # For demonstration, we fail if we do not see an error raised.
        pytest.fail("Expected a syntax error for reserved keywords used as identifiers")
    except SyntaxError:
        pass  # This is the expected outcome

@pytest.mark.spec
@pytest.mark.unit
def test_reserved_functions():
    """
    MEP-001 states that 'File()' and 'Git()' are reserved for special usage.
    Ensure they cannot be used as normal identifiers or misapplied.
    """
    source = "File = 'some file'\nGit = 'some repo'"
    with pytest.raises(SyntaxError):
        tokenize(source)

@pytest.mark.spec
@pytest.mark.xfail(reason="Spec not fully implemented – punctuation not fully enforced")
def test_reserved_punctuation():
    """
    Verifies that reserved punctuation (like ':' or '=') cannot be part of unquoted keys.
    """
    source = "some:key = 1"  # The colon here is invalid in an unquoted key
    with pytest.raises(SyntaxError):
        tokenize(source)

@pytest.mark.spec
@pytest.mark.xfail(reason="Spec not fully implemented – string quoting not fully enforced")
def test_string_quotation_rules():
    """
    Tests the variety of string quoting forms:
      - Single quotes
      - Double quotes
      - Triple single quotes
      - Triple double quotes
      - Backticks
      - F-strings
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
    tokens = tokenize(source)
    # We can check that multiple STRING tokens appear
    string_tokens = [t for t in tokens if t[0] == "STRING"]
    assert len(string_tokens) >= 6, "Expected multiple recognized strings in different forms"

@pytest.mark.spec
def test_arithmetic_operators():
    """
    Tests arithmetic operators: +, -, *, /, %, **
    """
    source = "value = 2 + 3 * 4 - 5 / 1 % 2 ** 3"
    tokens = tokenize(source)
    # Expect tokens for IDENTIFIER 'value', OPERATOR '=', and OPERATORs in the expression.
    op_tokens = [t for t in tokens if t[0] == "OPERATOR"]
    # We might expect 6 operators: = is punctuation, not an operator in this grammar.
    assert len(op_tokens) == 6  # +, *, -, /, %, **
    ops = [t[1] for t in op_tokens]
    # The presence of '**' might appear differently, verify as needed
    # (Some lexers might see '*' then '*')
    # Adjust as needed for your implementation logic.

@pytest.mark.spec
@pytest.mark.xfail(reason="Spec not fully implemented – pipeline operator not fully enforced")
def test_pipeline_operator():
    """
    Tests the pipeline operator usage: data | transform | filter
    """
    source = "result = (~ data | transform | filter ~)"
    tokens = tokenize(source)
    # Expect OPERATOR '|' multiple times, plus ~(...) usage
    pipeline_ops = [t for t in tokens if t[0] == "OPERATOR" and t[1] == "|"]
    assert len(pipeline_ops) == 2

@pytest.mark.spec
@pytest.mark.xfail(reason="Spec not fully implemented – ternary usage not fully enforced; Expressions not declared as of MEP-001.")
def test_conditional_ternary_operator():
    """
    Tests the inline conditional operator: "Active" if cond else "Inactive"
    """
    source = 'status = (~ "Active" if is_active else "Inactive" ~)'
    tokens = tokenize(source)
    # Expect KEYWORD tokens for 'if' and 'else', plus string tokens for "Active"/"Inactive"
    kw_tokens = [t for t in tokens if t[0] == "KEYWORD"]
    assert len(kw_tokens) == 2, "Expected 'if' and 'else' as KEYWORD tokens"

@pytest.mark.spec
@pytest.mark.xfail(reason="Spec not fully implemented – membership usage not fully enforced")
def test_membership_operators():
    """
    Tests membership 'in' and 'not in'
    """
    source = 'allowed = (~ "admin" in user.roles ~)'
    tokens = tokenize(source)
    in_tokens = [t for t in tokens if t[0] == "KEYWORD" and t[1] == "in"]
    assert len(in_tokens) == 1

@pytest.mark.spec
# @pytest.mark.xfail(reason="Spec not fully implemented – merge operator not fully enforced; Not declared until MEP-0015.")
def test_merge_operator():
    """
    Verifies usage of '<<' to merge tables or inline tables.
    """
    source = '''
    [settings]
    merged_config = default << user_override
    '''
    tokens = tokenize(source)
    merge_tokens = [t for t in tokens if t[0] == "OPERATOR" and t[1] == "<<"]
    assert len(merge_tokens) == 1

@pytest.mark.spec
@pytest.mark.xfail(reason="Spec not fully implemented – error checking not fully enforced")
def test_invalid_use_of_colon():
    """
    Confirms that using a colon as part of a key name triggers a syntax error.
    """
    source = 'invalid:key = "value"'
    with pytest.raises(SyntaxError):
        tokenize(source)

@pytest.mark.spec
@pytest.mark.xfail(reason="Spec not fully implemented – error checking not fully enforced")
def test_keyword_as_identifier():
    """
    Attempts to use a reserved keyword (e.g. 'if') as a variable name.
    Should cause a syntax error.
    """
    source = 'if = "condition"'
    with pytest.raises(SyntaxError):
        tokenize(source)

@pytest.mark.spec
@pytest.mark.xfail(reason="Spec not fully implemented – special functions usage not fully enforced")
def test_reserved_function_as_var():
    """
    Attempts to use 'File()' or 'Git()' as normal identifiers or variables.
    Should raise an error.
    """
    source = 'File = "somefile"'
    with pytest.raises(SyntaxError):
        tokenize(source)

@pytest.mark.spec
# @pytest.mark.xfail(reason="Spec not fully implemented – bracket usage not fully enforced")
def test_unmatched_brackets():
    """
    Should raise a syntax error when bracket pairs are mismatched or incomplete.
    """
    source = '[config'
    with pytest.raises(SyntaxError):
        tokenize(source)

@pytest.mark.spec
# @pytest.mark.xfail(reason="Spec not fully implemented – string interpolation rules not fully enforced")
def test_invalid_mismatched_quotes():
    """
    Confirms that mismatched quotes trigger a syntax error.
    """
    source = 'bad = "Missing end quote'
    with pytest.raises(SyntaxError):
        tokenize(source)

# You can add more tests for any other open issues or future reserved symbols as necessary.

def test_print_tokens_for_inspection():
    """
    Optional test: just prints out tokens for manual inspection; not xfailed.
    """
    sample = 'merged = default << user_override'
    tokens = tokenize(sample)
    pprint(tokens)
