# test_scoped_variables.py
import pytest

from jaml import (
    round_trip_loads,
    round_trip_dumps,
    render
)

from jaml import parser

@pytest.mark.spec
@pytest.mark.mep0012
# @pytest.mark.xfail(reason="Global scope variable resolution not fully implemented yet.")
def test_global_scope_variable_resolved():
    """
    MEP-012:
      @-scope should resolve variables defined globally (in [globals]) at load time.
    """
    toml_str = """
[globals]
base = "/home/user"

[paths]
config = f"@{globals.base}/config.toml"
"""
    # Round-trip to ensure the variable references remain intact
    ast = round_trip_loads(toml_str)
    reserialized = round_trip_dumps(ast)

    # The line should still contain "@{base}" reference
    assert 'config = f"@{globals.base}/config.toml"' in reserialized

    # Render final output
    rendered = render(reserialized)
    reserialized = round_trip_dumps(rendered)
    # Expect the global variable `base` to be replaced
    assert "/home/user/config.toml" in reserialized


@pytest.mark.spec
@pytest.mark.mep0012
# @pytest.mark.xfail(reason="Self scope override not fully enforced yet.")
def test_self_scope_overrides_global():
    """
    MEP-012:
      %{...} referencing a table-local variable should override any global with the same name.
    """
    toml_str = """
[globals]
name = "GlobalName"

[user]
name = "LocalName"
greeting = f"Hello, %{name}!"
"""
    # Render or parse -> re-serialize
    rendered = render(toml_str)
    reserialized = round_trip_dumps(rendered)
    # Since local scope overrides global, we expect "Hello, LocalName!"
    assert "Hello, LocalName!" in reserialized


@pytest.mark.spec
@pytest.mark.mep0012
# @pytest.mark.xfail(reason="Context scope resolution not fully implemented yet.")
def test_context_scope_render_time():
    """
    MEP-012:
      ${...} references variables provided by the context at render time.
    """
    toml_str = """
[logic]
summary = f"User: ${user.name}, Age: ${user.age}"
"""
    # Provide context at render-time:
    ctx = {
        "user": {
            "name": "Azzy",
            "age":  9
        }
    }
    rendered = render(toml_str, context=ctx)
    reserialized = round_trip_dumps(rendered)
    # Expect "User: Azzy, Age: 9"
    assert "User: Azzy, Age: 9" in reserialized


@pytest.mark.spec
@pytest.mark.mep0012
# @pytest.mark.xfail(reason="F-string dynamic style resolution not fully implemented yet.")
def test_f_string_dynamic_style():
    """
    MEP-012:
      Using f-string style (f"") with placeholders should produce the correct resolved string.
    """
    toml_str = """
[paths]
base = "/home/user"
config_path = f"@{paths.base}/config.toml"
"""
    rendered = render(toml_str)
    reserialized = round_trip_dumps(rendered) 
    assert "/home/user/config.toml" in reserialized


@pytest.mark.spec
@pytest.mark.mep0012
@pytest.mark.xfail(reason="Concatenation style resolution not fully implemented yet.")
def test_concatenation_style():
    """
    MEP-012:
      Using concatenation style (variable + literal) should produce the same result 
      as the f-string approach.
    """
    toml_str = """
[paths]
base = "/var/www"
config_path = @{paths.base} + "/myapp/config.toml"
"""
    rendered = render(toml_str)
    reserialized = round_trip_dumps(rendered)
    assert "/var/www/myapp/config.toml" in reserialized


@pytest.mark.spec
@pytest.mark.mep0012
@pytest.mark.xfail(reason="Partial expression evaluation for mixed styles not implemented yet.")
def test_mixed_styles_incomplete_implementation():
    """
    MEP-012:
      A single line that mixes f-string placeholders and + operator 
      might not be fully supported yet. Mark as xfail until done.
    """
    toml_str = """
[paths]
base = "/opt"
config_path = f"${base}" + "/dynamic/config.toml"
"""
    rendered = render(toml_str, context={"base": "/custom"})
    reserialized = round_trip_dumps(rendered)
    assert "/opt/dynamic/config.toml" in reserialized or "/custom/dynamic/config.toml" in reserialized


@pytest.mark.spec
@pytest.mark.mep0012
# @pytest.mark.xfail(reason="Global and context scope overshadow handling not fully implemented yet.")
def test_global_and_context_scope_same_name():
    """
    MEP-012:
      If a variable name is present in both global and context scope, 
      it should refer to whichever is considered primary. 
      This might be unimplemented or ambiguous for now -> xfail.
    """
    toml_str = """
[globals]
path = "/global/base"

[config]
file = f"${path}/config.toml"
"""
    ctx = {"path": "/render-time"}

    rendered = render(toml_str, context=ctx)
    reserialized = round_trip_dumps(rendered)
    assert "/render-time/config.toml" in reserialized

@pytest.mark.spec
@pytest.mark.mep0012
@pytest.mark.xfail(reason="Support for inline comments not fully implemented yet.")
def test_global_and_context_scope_same_name_and_inline_cmt():
    """
    MEP-012:
      If a variable name is present in both global and context scope, 
      it should refer to whichever is considered primary. 
      This might be unimplemented or ambiguous for now -> xfail.
    """
    toml_str = """
[globals]
path = "/global/base"

[config]
file = f"${path}/config.toml" # This comment may cause a failure
"""
    ctx = {"path": "/render-time"}

    rendered = render(toml_str, context=ctx)
    reserialized = round_trip_dumps(rendered)
    assert "/render-time/config.toml" in reserialized


