# test_scoped_variables.py
import pytest

from jaml import round_trip_loads


@pytest.mark.spec
@pytest.mark.mep0012
@pytest.mark.xfail(reason="Global scope variable resolution not fully implemented yet.")
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
    reserialized = ast.dumps()

    # The line should still contain "@{base}" reference
    assert 'config = f"@{globals.base}/config.toml"' in reserialized

    # Render final output
    data = round_trip_loads(toml_str)
    rendered = data.render()
    reserialized = rendered.dumps()
    # Expect the global variable `base` to be replaced
    assert "/home/user/config.toml" in reserialized


@pytest.mark.spec
@pytest.mark.mep0012
@pytest.mark.xfail(reason="Self scope override not fully enforced yet.")
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
    data = round_trip_loads(toml_str)
    rendered = data.render()
    reserialized = rendered.dumps()
    # Since local scope overrides global, we expect "Hello, LocalName!"
    assert "Hello, LocalName!" in reserialized


@pytest.mark.spec
@pytest.mark.mep0012
@pytest.mark.xfail(reason="Context scope resolution not fully implemented yet.")
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
    ctx = {"user": {"name": "Azzy", "age": 9}}

    data = round_trip_loads(toml_str)
    data.render(context=ctx)
    reserialized = data.render()
    # Expect "User: Azzy, Age: 9"
    assert "User: Azzy, Age: 9" in reserialized


@pytest.mark.spec
@pytest.mark.mep0012
@pytest.mark.xfail(
    reason="F-string dynamic style resolution not fully implemented yet."
)
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

    data = round_trip_loads(toml_str)
    rendered = data.render()
    reserialized = rendered.dumps()
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
    data = round_trip_loads(toml_str)
    rendered = data.render()
    reserialized = rendered.dumps()
    assert "/var/www/myapp/config.toml" in reserialized


@pytest.mark.spec
@pytest.mark.mep0012
@pytest.mark.xfail(
    reason="Partial expression evaluation for mixed styles not implemented yet."
)
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
    ctx = {"base": "/custom"}
    data = round_trip_loads(toml_str)
    reserialized = data.render(context=ctx).dumps()
    assert (
        "/opt/dynamic/config.toml" in reserialized
        or "/custom/dynamic/config.toml" in reserialized
    )


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
    data = round_trip_loads(toml_str)
    data.render(context=ctx)
    reserialized = data.dumps()
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

    data = round_trip_loads(toml_str)
    reserialized = data.render(context=ctx).dumps()
    assert "/render-time/config.toml" in reserialized
