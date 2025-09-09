# test_expression_folding.py
import pytest

from jaml import round_trip_loads, round_trip_dumps, render


@pytest.mark.spec
@pytest.mark.xfail(
    reason="Partial evaluation of mixed static/dynamic references not fully implemented."
)
def test_mixed_static_and_dynamic_fold():
    """
    MEP-0025:
      {^ ... ^} expression with both static (global/self) references
      and dynamic (context) references should partially evaluate
      at load time, leaving the context portion deferred.
    """
    toml_str = """
[server]
host = "prodserver"
port = 8080

[api]
endpoint = {^ "http://" + @{server.host} + ":" + @{server.port} + "/api?token=" + ${auth_token} ^}
"""
    # 1) Load (round_trip_loads) partially evaluates the folded expression.
    ast = round_trip_loads(toml_str)
    reserialized = round_trip_dumps(ast)

    # We expect that server.host/port are replaced, but ${auth_token} remains.
    assert "http://prodserver:8080/api?token=" in reserialized
    assert "${auth_token}" in reserialized

    # 2) Final render with context
    context = {"auth_token": "ABC123"}
    rendered = render(reserialized, context=context)
    # Should fully evaluate to a final string
    assert "http://prodserver:8080/api?token=ABC123" in rendered


@pytest.mark.spec
@pytest.mark.xfail(
    reason="Conditional folding may not fully simplify to context references yet."
)
def test_conditional_reduces_to_context():
    """
    MEP-0025:
      If a folded expression contains a conditional referencing only
      load-time variables on one side, that side is fully computed,
      possibly simplifying to a context variable reference.
    """
    toml_str = """
[logic]
is_production = false

[settings]
strategy = {^ "ProductionStrategy" if @{logic.is_production} else ${dynamic_strategy} ^}
"""
    ast = round_trip_loads(toml_str)
    reserialized = round_trip_dumps(ast)
    assert "strategy = {^ ${dynamic_strategy} ^}" in reserialized, (
        "Expression did not fold to the dynamic part."
    )

    context = {"dynamic_strategy": "Development"}
    rendered = render(reserialized, context=context)
    assert 'strategy = "Development"' in rendered


@pytest.mark.spec
@pytest.mark.xfail(
    reason="Boolean simplification rule ('true and') may not be enforced yet."
)
def test_true_and_simplification():
    """
    MEP-0025:
      The specification says if an expression contains "true and ${flag}",
      it should simplify to just ${flag}.
    """
    toml_str = """
[flags]
result = {^ true and ${flag} ^}
"""
    ast = round_trip_loads(toml_str)
    reserialized = round_trip_dumps(ast)
    # We expect it to simplify to {^ ${flag} ^}
    assert "result = {^ ${flag} ^}" in reserialized, (
        "'true and' wasn't removed in the fold step."
    )

    context = {"flag": "enabled"}
    rendered = render(reserialized, context=context)
    assert 'result = "enabled"' in rendered


@pytest.mark.spec
@pytest.mark.xfail(reason="Load-time error for undefined globals not fully enforced.")
def test_undefined_global_causes_error_in_fold():
    """
    MEP-0025:
      If a {^ ... ^} expression references a global or self variable
      that doesn't exist, an error must be raised at load time.
    """
    invalid_toml = """
[bad]
value = {^ @{nonexistent} + ${some_flag} ^}
"""
    with pytest.raises(Exception, match="undefined variable 'nonexistent'"):
        round_trip_loads(invalid_toml)


@pytest.mark.spec
@pytest.mark.xfail(
    reason="Render-time error for missing context variable not implemented."
)
def test_missing_context_variable_fails_at_render():
    """
    MEP-0025:
      If a context variable is still needed after partial evaluation,
      but is not supplied at render, we raise an error at render time.
    """
    toml_str = """
[api]
endpoint = {^ "http://" + @{host} + "/service?key=" + ${secret_key} ^}
[api.host]
host = "example.com"
"""
    ast = round_trip_loads(toml_str)
    with pytest.raises(Exception, match="missing context variable 'secret_key'"):
        render(round_trip_dumps(ast), context={})  # no secret_key


@pytest.mark.spec
@pytest.mark.xfail(
    reason="Nested partial expressions might not yet be combined correctly."
)
def test_nested_expressions_combine_static_and_dynamic():
    """
    MEP-0025:
      Expressions can nest further computations, e.g. {^ @{base} + ( {^ another expr ^} ) ^}
      verifying partial folds inside partial folds.
    """
    toml_str = """
[env]
base = "HOME/"

[config]
nested = {^ @{base} + {^ ${context_val} + ".cfg" ^} ^}
"""
    ast = round_trip_loads(toml_str)
    reserialized = round_trip_dumps(ast)
    assert "HOME/" in reserialized
    assert '{^ ${context_val} + ".cfg" ^}' in reserialized

    context = {"context_val": "DB"}
    rendered = render(reserialized, context=context)
    assert 'nested = "HOME/DB.cfg"' in rendered


@pytest.mark.spec
@pytest.mark.xfail(reason="Complex multi-operator precedence not fully supported yet")
def test_operator_precedence_in_folded_expressions():
    """
    MEP-0025:
      Operator precedence can be tricky if partial sub-expressions are folded.
      Mark xfail until fully implemented or tested thoroughly.
    """
    toml_str = """
[calc]
value = {^ (@{n} + 5) * 2 + ${x} / 3 ^}
[calc.n]
n = 10
"""
    ast = round_trip_loads(toml_str)
    reserialized = round_trip_dumps(ast)
    assert "30 + ${x} / 3" in reserialized

    rendered = render(reserialized, context={"x": 6})
    assert "value = 32" in rendered


@pytest.mark.spec
@pytest.mark.xfail(
    reason="Flattening nested booleans (e.g. 'false or ${flag}') not implemented."
)
def test_nested_boolean_simplification():
    """
    MEP-0025:
      If an expression folds to something like 'false or ${flag}',
      it might be simplified further, or remain partial.
    """
    toml_str = """
[bools]
is_always_true = false

[flags]
value = {^ @{bools.is_always_true} or ${ctx_flag} ^}
"""
    ast = round_trip_loads(toml_str)
    reserialized = round_trip_dumps(ast)
    assert "value = {^ ${ctx_flag} ^}" in reserialized
