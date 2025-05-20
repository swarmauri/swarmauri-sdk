# test_expressions.py
import pytest

from jaml import (
    round_trip_loads,
    round_trip_dumps,
)


@pytest.mark.spec
@pytest.mark.xfail(reason="Load-time string concatenation not fully implemented.")
def test_simple_string_concat_expression():
    """
    MEP-0022:
      A {~ ... ~} expression that concatenates strings (with + operator)
      should be evaluated at load time, yielding a plain string without extra quotes.
    """
    toml_str = """
[paths]
base = "/usr/local"
config = {~ @{base} + "/config.toml" ~}
"""
    # We'll parse and presumably your system does immediate evaluation
    # for {~ ~} expressions.
    ast = round_trip_loads(toml_str)
    # Now the expression should be replaced with the resulting string "/usr/local/config.toml"

    # Also check round-trip output if you keep expressions or if they're replaced:
    reserialized = round_trip_dumps(ast)
    # The spec says the result is inserted as plain value, so
    # we expect something like: `config = "/usr/local/config.toml"`
    assert "/usr/local/config.toml" in reserialized, (
        "Expected the expression to be replaced with its evaluated string result."
    )


@pytest.mark.spec
@pytest.mark.xfail(reason="Arithmetic evaluation not yet fully integrated.")
def test_arithmetic_expression():
    """
    MEP-0022:
      A {~ ... ~} expression can perform arithmetic operations and
      store the final numeric result at load time.
    """
    toml_str = """
[settings]
default_retries = 3
max_retries = {~ @{default_retries} * 2 ~}
"""
    ast = round_trip_loads(toml_str)
    reserialized = round_trip_dumps(ast)
    # The expression {~ 3 * 2 ~} should evaluate to 6, inserted as a plain integer.
    assert "max_retries = 6" in reserialized, (
        "Arithmetic expression did not evaluate to integer at load time."
    )


@pytest.mark.spec
@pytest.mark.xfail(reason="Conditional expression evaluation not fully supported yet.")
def test_conditional_expression():
    """
    MEP-0022:
      A {~ ... ~} expression may include a conditional (ternary) style expression,
      e.g. "X if condition else Y". The result is inserted at load time.
    """
    toml_str = """
[system]
debug_mode = false
log_level: str = {~ "DEBUG" if false else "INFO" ~}
"""
    ast = round_trip_loads(toml_str)
    reserialized = round_trip_dumps(ast)
    # Because the conditional is 'false', the result should be "INFO".
    assert 'log_level: str = "INFO"' in reserialized, (
        "Conditional expression did not evaluate to 'INFO'."
    )


@pytest.mark.spec
@pytest.mark.xfail(
    reason="List comprehension support for expressions not fully implemented."
)
def test_list_comprehension_expression():
    """
    MEP-0022:
      A {~ ... ~} expression supports list comprehensions,
      producing a final list at load time.
    """
    toml_str = """
[data]
values = {~ [ x * 2 for x in [1, 2, 3] ] ~}
"""
    ast = round_trip_loads(toml_str)
    reserialized = round_trip_dumps(ast)
    # The final list should be [2, 4, 6].
    assert "[2, 4, 6]" in reserialized, (
        "List comprehension result not properly inserted into final output."
    )


@pytest.mark.spec
@pytest.mark.xfail(
    reason="Context scope disallowed in load-time expressions not enforced yet."
)
def test_scope_restrictions_disallow_context_scope():
    """
    MEP-0022 Section 3.3:
      Context scope (${...}) is disallowed in {~ ... ~} expressions.
      Attempting to use it should raise a descriptive error.
    """
    invalid_toml = """
[invalid]
value = {~ ${external} + 10 ~}
"""
    with pytest.raises(
        Exception, match="context variables are not allowed in load-time expressions"
    ):
        round_trip_loads(invalid_toml)


@pytest.mark.spec
@pytest.mark.xfail(reason="not fully implemented.")
def test_undefined_variable_raises_error():
    """
    MEP-0022:
      If an expression references a variable that doesn't exist in
      global or local scope, the parser must raise a descriptive error.
    """
    invalid_toml = """
[broken]
value = {~ @{nonexistent} * 2 ~}
"""
    with pytest.raises(Exception, match="undefined variable 'nonexistent'"):
        round_trip_loads(invalid_toml)


@pytest.mark.spec
@pytest.mark.xfail(
    reason="Syntax error reporting within expressions not fully implemented."
)
def test_syntax_error_in_expression():
    """
    MEP-0022:
      A syntax error within {~ ... ~} should produce a clear error
      indicating the location and nature of the problem.
    """
    invalid_toml = """
[broken]
value = {~ "str" if 1 else ~}
"""
    with pytest.raises(Exception, match="Syntax error in expression"):
        round_trip_loads(invalid_toml)


@pytest.mark.spec
@pytest.mark.xfail(
    reason="Operator precedence in load-time expressions not fully implemented."
)
def test_operator_precedence_in_expression():
    """
    MEP-0022:
      Complex expressions require well-defined operator precedence
      to avoid ambiguity. For now, mark xfail if not fully implemented.
    """
    toml_str = """
[calc]
result = {~ 2 + 3 * 5 ~}  # Expect 2 + (3*5) = 17 if precedence follows normal arithmetic
"""
    ast = round_trip_loads(toml_str)
    reserialized = round_trip_dumps(ast)
    assert "result = 17" in reserialized, (
        "Operator precedence not applied correctly (expected 17)."
    )
