import pytest
from jaml import loads, dumps, round_trip_loads, round_trip_dumps

# Test 2: Global Scope Evaluation
@pytest.mark.spec
@pytest.mark.mep0011
# @pytest.mark.xfail(reason="Global scope evaluation not implemented")
def test_global_scope_default_evaluation():
    """
    In f-string interpolations, we should replace global scope on load.
    """
    toml_str = """
base = "/home/user"

[config]
url = f"@{base}/config.toml"
"""
    data = round_trip_loads(toml_str)
    assert data["config"]["url"] == "/home/user/config.toml"
    out = round_trip_dumps(data)
    data_again = loads(out)
    assert data_again["config"]["url"] == "/home/user/config.toml"

@pytest.mark.spec
@pytest.mark.mep0011
# @pytest.mark.xfail(reason="Global scope evaluation not implemented")
def test_global_scope_section_evaluation():
    """
    In f-string interpolations, we should replace global scope on load.
    """
    toml_str = """
[path]
base = "/home/user"

[config]
url = f"@{path.base}/config.toml"
"""
    data = round_trip_loads(toml_str)
    assert data["config"]["url"] == "/home/user/config.toml"
    out = round_trip_dumps(data)
    data_again = loads(out)
    assert data_again["config"]["url"] == "/home/user/config.toml"

# Test 3: Self (Local) Scope Evaluation
@pytest.mark.spec
@pytest.mark.mep0011
@pytest.mark.xfail(reason="Self scope evaluation not implemented")
def test_self_scope_evaluation():
    toml_str = """
[globals]
base = "/home/user"

[user]
name = "Alice"
greeting = f"Hello, %{name}!"
"""
    data = round_trip_loads(toml_str)
    assert data["user"]["greeting"] == "Hello, Alice!"
    out = round_trip_dumps(data)
    data_again = loads(out)
    assert data_again["user"]["greeting"] == "Hello, Alice!"

# Test 4: Context Scope Deferred Evaluation
@pytest.mark.spec
@pytest.mark.mep0011
@pytest.mark.xfail(reason="Context scope deferred evaluation not implemented")
def test_context_scope_deferred():
    toml_str = """
[logic]
summary = f"User: ${user.name}, Age: ${user.age}"
"""
    # Without context, placeholders remain unresolved.
    data = round_trip_loads(toml_str)
    assert data["logic"]["summary"] == "User: ${user.name}, Age: ${user.age}"
    # With a render context provided:

    out = round_trip_dumps(data)
    data_with_context = loads(out, context={"user.name": "Alice", "user.age": 30})
    assert data_with_context["logic"]["summary"] == "User: Alice, Age: 30"

# Test 5: F-String Interpolation
@pytest.mark.spec
@pytest.mark.mep0011
@pytest.mark.xfail(reason="F-string interpolation evaluation not implemented")
def test_fstring_interpolation():
    toml_str = """
[message]
text = f"Hello, {name}!"
"""
    # Assuming 'name' is provided via render context.
    data = round_trip_loads(toml_str, context={"name": "Alice"})
    assert data["message"]["text"] == "Hello, Alice!"
    out = round_trip_dumps(data)
    data_again = loads(out, context={"name": "Alice"})
    assert data_again["message"]["text"] == "Hello, Alice!"

# Test 6: Immediate Expression Evaluation using <{ ... }>
@pytest.mark.spec
@pytest.mark.mep0011
@pytest.mark.xfail(reason="Immediate expression evaluation not implemented")
def test_immediate_expression():
    toml_str = """
[paths]
base = "/usr/local"
config = <{ @{base} + '/config.toml' }>
"""
    data = round_trip_loads(toml_str)
    assert data["paths"]["config"] == "/usr/local/config.toml"
    out = round_trip_dumps(data)
    data_again = loads(out)
    assert data_again["paths"]["config"] == "/usr/local/config.toml"

# Test 7: Folded Expression Evaluation using <( ... )>
@pytest.mark.spec
@pytest.mark.mep0011
@pytest.mark.xfail(reason="Folded expression evaluation not implemented")
def test_folded_expression():
    toml_str = """
[server]
host = "prodserver"
port = "8080"

[api]
endpoint = <( "http://" + @{server.host} + ":" + @{server.port} + "/api?token=" + ${auth_token} )>
"""
    # Provide context for the deferred part.
    data = round_trip_loads(toml_str, context={"auth_token": "ABC123"})
    assert data["api"]["endpoint"] == "http://prodserver:8080/api?token=ABC123"
    out = round_trip_dumps(data)
    data_again = loads(out, context={"auth_token": "ABC123"})
    assert data_again["api"]["endpoint"] == "http://prodserver:8080/api?token=ABC123"

# Test 8: List Comprehension Evaluation
@pytest.mark.spec
@pytest.mark.mep0011
@pytest.mark.xfail(reason="List comprehension evaluation not implemented")
def test_list_comprehension():
    toml_str = """
[items]
list_config = [f"item_{x}" for x in [1, 2, 3]]
"""
    data = round_trip_loads(toml_str)
    assert data["items"]["list_config"] == ["item_1", "item_2", "item_3"]
    out = round_trip_dumps(data)
    data_again = loads(out)
    assert data_again["items"]["list_config"] == ["item_1", "item_2", "item_3"]

# Test 9: Dict Comprehension Evaluation
@pytest.mark.spec
@pytest.mark.mep0011
@pytest.mark.xfail(reason="Dict comprehension evaluation not implemented")
def test_dict_comprehension():
    toml_str = """
[items]
dict_config = {f"key_{x}": x * 2 for x in [1, 2, 3]}
"""
    data = round_trip_loads(toml_str)
    assert data["items"]["dict_config"] == {"key_1": 2, "key_2": 4, "key_3": 6}
    out = round_trip_dumps(data)
    data_again = loads(out)
    assert data_again["items"]["dict_config"] == {"key_1": 2, "key_2": 4, "key_3": 6}

# Test 10: Arithmetic Operations in Expressions
@pytest.mark.spec
@pytest.mark.mep0011
@pytest.mark.xfail(reason="Arithmetic operations in expressions not implemented")
def test_arithmetic_operations():
    toml_str = """
[calc]
result = <{ 3 + 4 }>
"""
    data = round_trip_loads(toml_str)
    assert data["calc"]["result"] == 7
    out = round_trip_dumps(data)
    data_again = loads(out)
    assert data_again["calc"]["result"] == 7

# Test 11: Conditional Logic in Expressions
@pytest.mark.spec
@pytest.mark.mep0011
@pytest.mark.xfail(reason="Conditional logic evaluation not implemented")
def test_conditional_logic():
    toml_str = """
[cond]
status = f"{'Yes' if true else 'No'}"
"""
    data = round_trip_loads(toml_str)
    assert data["cond"]["status"] == "Yes"
    out = round_trip_dumps(data)
    data_again = loads(out)
    assert data_again["cond"]["status"] == "Yes"

# Is this really a type inference test? 
@pytest.mark.spec
@pytest.mark.mep0011
@pytest.mark.xfail(reason="Inference in expressions not fully implemented")
def test_infer_expressions():
    """
    Ensures expressions (wrapped with <{ ... )>) are type-inferred from their result.
    """
    source = '''
    [exprs]
    # Arithmetic expression
    sum_val = <{ 10 + 5 }>
    # String concatenation
    greeting = <{ "Hello, " + "World!" }>
    # Boolean logic
    combo = <{ true and false }>
    '''
    data = round_trip_loads(source)
    exprs = data["exprs"]
    assert isinstance(exprs["sum_val"], int)
    assert exprs["sum_val"] == 15
    assert isinstance(exprs["greeting"], str)
    assert exprs["greeting"] == "Hello, World!"
    assert isinstance(exprs["combo"], bool)
    assert exprs["combo"] is False

    out = round_trip_dumps(data)
    round_trip_data = loads(out)
    exprs_round_trip = round_trip_data["exprs"]
    assert isinstance(exprs_round_trip["sum_val"], int)
    assert exprs_round_trip["sum_val"] == 15
    assert isinstance(exprs_round_trip["greeting"], str)
    assert exprs_round_trip["greeting"] == "Hello, World!"
    assert isinstance(exprs_round_trip["combo"], bool)
    assert exprs_round_trip["combo"] is False