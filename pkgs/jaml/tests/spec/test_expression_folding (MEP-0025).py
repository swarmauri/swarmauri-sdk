# test_expression_folding.py
import pytest

from jaml import (
    round_trip_loads,
    round_trip_dumps,
    render
)


@pytest.mark.spec
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
    # Something like: endpoint = {^ "http://prodserver:8080/api?token=" + ${auth_token} ^}
    assert "http://prodserver:8080/api?token=" in reserialized
    assert "${auth_token}" in reserialized

    # 2) Final render with context
    context = {"auth_token": "ABC123"}
    rendered = render(reserialized, context=context)
    # Should fully evaluate to a final string
    assert "http://prodserver:8080/api?token=ABC123" in rendered


@pytest.mark.spec
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
    # After load, it should simplify to {^ ${dynamic_strategy} ^}
    ast = round_trip_loads(toml_str)
    reserialized = round_trip_dumps(ast)
    assert "strategy = {^ ${dynamic_strategy} ^}" in reserialized, \
        "Expression did not fold to the dynamic part."

    # Now final render
    context = {"dynamic_strategy": "Development"}
    rendered = render(reserialized, context=context)
    # The final config should have "strategy = \"Development\""
    assert "strategy = \"Development\"" in rendered


@pytest.mark.spec
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
    # After partial load, the 'true and' is recognized as redundant.
    # We'll see if your partial evaluation step removes it automatically 
    # or if it remains until the final unparse. 
    ast = round_trip_loads(toml_str)
    reserialized = round_trip_dumps(ast)

    # We expect it to simplify to {^ ${flag} ^}
    # If your system doesn't store the partial expression as text, 
    # it might just remain the same. The spec says it "should" be simplified,
    # so let's check for it.
    assert "result = {^ ${flag} ^}" in reserialized, \
        "'true and' wasn't removed in the fold step."

    # Final render with a context variable
    context = {"flag": "enabled"}
    rendered = render(reserialized, context=context)
    assert "result = \"enabled\"" in rendered


@pytest.mark.spec
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
    # This should parse fine at load time (the host is found).
    ast = round_trip_loads(toml_str)
    # But if we fail to provide 'secret_key' at render time, it's an error.
    with pytest.raises(Exception, match="missing context variable 'secret_key'"):
        render(round_trip_dumps(ast), context={})  # no secret_key


@pytest.mark.spec
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
    # Step 1) partial load
    ast = round_trip_loads(toml_str)
    reserialized = round_trip_dumps(ast)
    # We expect the outer expression to incorporate "HOME/", while the inner remains dynamic.
    # The result might look like:
    # nested = {^ "HOME/" + {^ ${context_val} + ".cfg" ^} ^}
    assert "HOME/" in reserialized
    assert "{^ ${context_val} + \".cfg\" ^}" in reserialized

    # Step 2) final render
    context = {"context_val": "DB"}
    rendered = render(reserialized, context=context)
    # The final result should be "HOME/DB.cfg"
    assert "nested = \"HOME/DB.cfg\"" in rendered


@pytest.mark.xfail(reason="Complex multi-operator precedence not fully supported yet")
@pytest.mark.spec
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
    # At load time, (@{n}+5)*2 => (10+5)*2 => 30
    # So the expression might become {^ 30 + ${x} / 3 ^}
    assert "30 + ${x} / 3" in reserialized

    # Final evaluate with x=6 => 30 + 6/3 => 32
    rendered = render(reserialized, context={"x": 6})
    assert "value = 32" in rendered


@pytest.mark.xfail(reason="No specialized flattening for nested booleans implemented yet")
@pytest.mark.spec
def test_nested_boolean_simplification():
    """
    MEP-0025:
      If an expression folds to something like 'false or ${flag}', 
      it might be simplified further, or remain partial. 
      Mark xfail if not yet implemented.
    """
    toml_str = """
[bools]
is_always_true = false

[flags]
value = {^ @{bools.is_always_true} or ${ctx_flag} ^}
"""
    # We expect the load-time portion false => expression might become:
    # {^ ${ctx_flag} ^}
    ast = round_trip_loads(toml_str)
    reserialized = round_trip_dumps(ast)
    assert "value = {^ ${ctx_flag} ^}" in reserialized
