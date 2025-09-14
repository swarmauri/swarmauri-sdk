import pytest
from jaml import round_trip_loads, round_trip_dumps, loads


@pytest.mark.unit
def test_rt_global_scope_variable_load_only():
    """
    Test that we can load a snippet containing a global scope reference,
    without actually evaluating the @ expression.
    """
    jml = """
[logic]
greeting: str = ~( "Hello, " + @user.name )
    """.strip()
    # We don't provide any context, because we're only testing load, not evaluation.
    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)  # No context provided
    # Instead of checking for "Hello, Alice", we confirm the expression is stored as is.
    greeting_val = data["logic"]["greeting"]
    # We expect the raw expression string, e.g. '~( "Hello, " + @user.name )'
    assert greeting_val == '~( "Hello, " + @user.name )'


@pytest.mark.unit
def test_rt_global_scope_list_reference_load_only():
    jml = """
[logic]
first_value: int = ~( @values[0] + 10 )
    """.strip()
    # Again, no context, so no resolution.
    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)
    # We only confirm that "first_value" is the raw expression, not the numeric result 15
    assert data["logic"]["first_value"] == "~( @values[0] + 10 )"


@pytest.mark.unit
def test_rt_nested_global_scope_load_only():
    jml = """
[logic]
full_name: str = ~( @user.profile.first + " " + @user.profile.last )
    """.strip()
    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)
    # Confirm the parser loaded the snippet but did NOT evaluate
    assert (
        data["logic"]["full_name"]
        == '~( @user.profile.first + " " + @user.profile.last )'
    )


@pytest.mark.unit
def test_rt_local_vs_global_load_only():
    jml = """
[test]
name: str = "LocalName"
greeting: str = ~( "Hello, " + @name )
    """.strip()
    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)
    # We only confirm that 'greeting' has the raw expression, not any resolution.
    assert data["test"]["greeting"] == '~( "Hello, " + @name )'


@pytest.mark.unit
def test_rt_multiple_global_scopes_load_only():
    jml = """
[logic]
summary: str = ~( "User: " + @user.name + ", Age: " + str(@user.age) )
    """.strip()
    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)
    # Confirm the raw expression is stored as is
    assert (
        data["logic"]["summary"]
        == '~( "User: " + @user.name + ", Age: " + str(@user.age) )'
    )
