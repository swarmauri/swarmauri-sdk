# test_scoped_variables.py
import pytest

from jaml import (
    round_trip_loads,
    round_trip_dumps,
    render
)

from jaml import parser

@pytest.mark.spec
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
config = f"@{base}/config.toml"
"""
    # Round-trip to ensure the variable references remain intact
    ast = round_trip_loads(toml_str)
    reserialized = round_trip_dumps(ast)

    # The line should still contain "@{base}" reference
    assert "config = f\"@{base}/config.toml\"" in reserialized

    # Render final output
    rendered = render(toml_str, context={})
    # Expect the global variable `base` to be replaced
    assert "/home/user/config.toml" in rendered, \
        "Global scope variable not correctly resolved in final output."


@pytest.mark.spec
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
    rendered = render(toml_str, context={})
    # Since local scope overrides global, we expect "Hello, LocalName!"
    assert "Hello, LocalName!" in rendered, \
        "Local/self variable did not override global variable as specified."


@pytest.mark.spec
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
        "user.name": "Azzy",
        "user.age":  9
    }
    rendered = render(toml_str, context=ctx)
    # Expect "User: Azzy, Age: 9"
    assert "User: Azzy, Age: 9" in rendered, \
        "Context scope variables not correctly resolved during render time."


@pytest.mark.spec
# @pytest.mark.xfail(reason="F-string dynamic style resolution not fully implemented yet.")
def test_f_string_dynamic_style():
    """
    MEP-012:
      Using f-string style (f"") with placeholders should produce the correct resolved string.
    """
    toml_str = """
[paths]
base = "/home/user"
config_path = f"@{base}/config.toml"
"""
    rendered = render(toml_str, context={})
    # Expect "/home/user/config.toml"
    assert "/home/user/config.toml" in rendered


@pytest.mark.spec
# @pytest.mark.xfail(reason="Concatenation style resolution not fully implemented yet.")
def test_concatenation_style():
    """
    MEP-012:
      Using concatenation style (variable + literal) should produce the same result 
      as the f-string approach.
    """
    toml_str = """
[paths]
base = "/var/www"
config_path = @{base} + "/myapp/config.toml"
"""
    rendered = render(toml_str, context={})
    # Expect "/var/www/myapp/config.toml"
    assert "/var/www/myapp/config.toml" in rendered


@pytest.mark.spec
# @pytest.mark.xfail(reason="Partial expression evaluation for mixed styles not implemented yet.")
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
    # Expect either "/opt/dynamic/config.toml" if using the global 'base',
    # or "/custom/dynamic/config.toml" if context overshadow global.
    assert "/opt/dynamic/config.toml" in rendered or "/custom/dynamic/config.toml" in rendered


@pytest.mark.spec
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
file = f"${path}/config.toml"   # Possibly overshadowed by context
"""
    ctx = {"path": "/render-time"}  # If context overshadow is expected

    rendered = render(toml_str, context=ctx)
    # Expect context overshadowing to yield "/render-time/config.toml"
    assert "/render-time/config.toml" in rendered


