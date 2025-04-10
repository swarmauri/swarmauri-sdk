import pytest
from jaml import loads, dumps, round_trip_loads, round_trip_dumps, resolve, render
from jaml.lark_nodes import PreservedString

# Test 2: Global Scope Evaluation
@pytest.mark.spec
@pytest.mark.mep0011
# @pytest.mark.xfail(reason="Global scope evaluation not implemented")
def test_global_scope_default_evaluation():
    """
    In f-string interpolations, we should replace global scope on load.
    """
    sample = """
base = "/home/user"
alt = "/home/alt"

[config]
url = f"@{base}/config.toml"
"""
    data = round_trip_loads(sample)
    assert data["config"]["url"] == 'f"@{base}/config.toml"'
    print("[DEBUG]:")
    print(data)

    data["config"]["url"] = PreservedString(value='f"@{alt}/config.toml"', original='f"@{alt}/config.toml"')
    print("[DEBUG]:")
    print(data)

    resolved_config = resolve(data)
    print("[DEBUG]:")
    print(resolved_config)
    assert resolved_config["config"]["url"] == "/home/alt/config.toml"

    out = round_trip_dumps(data)
    rendered_data = render(out)
    print("[DEBUG]:")
    print(rendered_data)
    assert rendered_data["config"]["url"] == "/home/alt/config.toml"

@pytest.mark.spec
@pytest.mark.mep0011
# @pytest.mark.xfail(reason="Global scope evaluation not implemented")
def test_global_scope_section_evaluation():
    """
    In f-string interpolations, we should replace global scope on load.
    """
    sample = """
[paths]
base = "/home/user"
alt = "/home/alt"

[config]
url = f"@{paths.base}/config.toml"
"""
    data = round_trip_loads(sample)
    assert data["config"]["url"] == 'f"@{paths.base}/config.toml"'
    print("[DEBUG]:")
    print(data)

    data["config"]["url"].original = 'f"@{paths.alt}/config.toml"'
    print("[DEBUG]:")
    print(data)


    resolved_config = resolve(data)
    print("[DEBUG]:")
    print(resolved_config)
    assert resolved_config["config"]["url"] == "/home/alt/config.toml"

    out = round_trip_dumps(data)
    rendered_data = render(out)
    print("[DEBUG]:")
    print(rendered_data)
    assert rendered_data["config"]["url"] == "/home/alt/config.toml"

# Test 3: Self (Local) Scope Evaluation
@pytest.mark.spec
@pytest.mark.mep0011
# @pytest.mark.xfail(reason="Self scope evaluation not implemented")
def test_self_scope_evaluation():
    sample = """
[globals]
base = "/home/user"

[user]
name = "Alice"
altname = "Bob"
greeting = f"Hello, %{name}!"
"""
    data = round_trip_loads(sample)
    assert data["user"]["greeting"] == 'f"Hello, %{name}!"'
    print("[DEBUG]:")
    print(data)

    data["user"]["greeting"].original = 'f"Hello, %{altname}!"'
    print("[DEBUG]:")
    print(data)

    resolved_config = resolve(data)
    print("[DEBUG]:")
    print(resolved_config)
    assert resolved_config["user"]["greeting"] == "Hello, Bob!"

    out = round_trip_dumps(data)
    rendered_data = render(out)
    print("[DEBUG]:")
    print(rendered_data)
    assert rendered_data["user"]["greeting"] == "Hello, Bob!"

# Test 4: Context Scope Deferred Evaluation
@pytest.mark.spec
@pytest.mark.mep0011
# @pytest.mark.xfail(reason="Context scope deferred evaluation not implemented")
def test_context_scope_deferred():
    sample = """
[logic]
summary = f"User: ${user.name}, Age: ${user.age}"
"""
    # Without context, placeholders remain unresolved.
    data = round_trip_loads(sample)
    assert data["logic"]["summary"] == 'f"User: ${user.name}, Age: ${user.age}"'
    # With a render context provided:

    resolved_config = resolve(data)
    print("[DEBUG]:")
    print(resolved_config)
    assert resolved_config["logic"]["summary"] == 'f"User: ${user.name}, Age: ${user.age}"'

    out = round_trip_dumps(data)
    rendered_data = render(out, context={"user": {"name": "Alice", "age": 30}})
    assert rendered_data["logic"]["summary"] == "User: Alice, Age: 30"

# Test 5: F-String Interpolation
@pytest.mark.spec
@pytest.mark.mep0011
# @pytest.mark.xfail(reason="F-string interpolation evaluation not fully implemented.")
def test_fstring_interpolation():
    sample = """
[message]
text = f"Hello, ${name}!"
"""
    # Assuming 'name' is provided via render context.
    data = round_trip_loads(sample)
    out = round_trip_dumps(data)

    resolved_config = resolve(data)
    print("[DEBUG]:")
    print(resolved_config)
    assert resolved_config["message"]["text"] == 'f"Hello, ${name}!"'


    rendered_data = render(out, context={"name": "Alice"})
    assert rendered_data["message"]["text"] == "Hello, Alice!"

    data_again = loads(out)
    assert data_again["message"]["text"] == 'f"Hello, ${name}!"'

# # Test 6: Deferred Expression Evaluation using <{ ... }>
# @pytest.mark.spec
# @pytest.mark.mep0011
# # @pytest.mark.xfail(reason="Deferred expression evaluation not implemented")
# def test_deferred_expression():
#     """
#     Validates deferred (ie: literal) expressions
#     """
#     sample = """
# [paths]
# base = "/usr/local"
# config = <{ %{base} + '/config.toml' }>
# """
#     data = round_trip_loads(sample)
#     assert data["paths"]["config"] == "%{base} + '/config.toml'"
#     out = round_trip_dumps(data)
#     rendered_data = render(out)
#     assert rendered_data["paths"]["config"] == "/usr/local/config.toml"

@pytest.mark.spec
@pytest.mark.mep0011
# @pytest.mark.xfail(reason="expression evaluation not implemented")
def test_expression():
    """
    Validates expressions
    """
    sample = """
[server]
host = "prodserver"
port = "8080"
devhost = "devserver"

[api]
endpoint = <( "http://" + @{server.host} + ":" + @{server.port} + "/api?token=" + ${auth_token} )>
"""
    # Provide context for the deferred part.
    data = round_trip_loads(sample)
    print("[DEBUG]:")
    print(data)
    assert data["api"]["endpoint"] == '<( "http://" + @{server.host} + ":" + @{server.port} + "/api?token=" + ${auth_token} )>'

    data["api"]["endpoint"].original = '<( "http://" + @{server.devhost} + ":" + @{server.port} + "/api?token=" + ${auth_token} )>'
    print("[DEBUG]:")
    print(data)

    resolved_config = resolve(data)
    print("[DEBUG]:")
    print(resolved_config)
    assert resolved_config["api"]["endpoint"] == "http://devserver:8080/api?token=${auth_token}"

    out = round_trip_dumps(data)
    data_again = render(out, context={"auth_token": "ABC123"})
    print("[DEBUG]:")
    print(data_again)
    assert data_again["api"]["endpoint"] == "http://devserver:8080/api?token=ABC123"

# Test 8: List Comprehension Evaluation
@pytest.mark.spec
@pytest.mark.mep0011
# @pytest.mark.xfail(reason="List comprehension evaluation not implemented")
def test_list_comprehension():
    sample = """
[items]
list_config = [f"item_{x}" for x in [1, 2, 3]]
"""
    data = round_trip_loads(sample)
    print("[DEBUG]:")
    print(data)
    assert data["items"]["list_config"] == '[f"item_{x}" for x in [1, 2, 3]]'


    data["items"]["list_config"].original = '[f"item_{x}" for x in [5, 10, 15]]'
    print("[DEBUG]:")
    print(data)

    resolved_config = resolve(data)
    print("[DEBUG]:")
    print(resolved_config)
    assert resolved_config["items"]["list_config"] == ["item_5", "item_10", "item_15"]

    out = round_trip_dumps(data)
    rendered_data = render(out)
    print("[DEBUG]:")
    print(rendered_data)
    assert rendered_data["items"]["list_config"] == ["item_5", "item_10", "item_15"]

# Test 9: Dict Comprehension Evaluation
@pytest.mark.spec
@pytest.mark.mep0011
# @pytest.mark.xfail(reason="Dict comprehension evaluation not implemented")
def test_dict_dot_notation_comprehension():
    """
    Comprehensions should defer evaluation
    """
    sample = """
[items]
dict_config = {f"key_{x}" : x * 2 for x in [1, 2, 3]}
"""
    data = round_trip_loads(sample)
    print("[DEBUG]:")
    print(data)
    assert data["items"]["dict_config"] == '{f"key_{x}" : x * 2 for x in [1, 2, 3]}'

    data["items"]["dict_config"].original = '{f"item_{x}": x * 3 for x in [5, 10, 15]}'
    print("[DEBUG]:")
    print(data)

    resolved_config = resolve(data)
    print("[DEBUG]:")
    print(resolved_config)
    assert resolved_config["items"]["dict_config"] == {"item_5": 15, "item_10": 30, "item_15": 45}


    out = round_trip_dumps(data)
    rendered_data = render(out)
    print("[DEBUG]:")
    print(rendered_data)
    assert rendered_data["items"]["dict_config"] == {"item_5": 15, "item_10": 30, "item_15": 45}

@pytest.mark.spec
@pytest.mark.mep0011
# @pytest.mark.xfail(reason="Dict comprehension evaluation not implemented")
def test_dict_assignment_comprehension():
    """
    Comprehensions should defer evaluation
    """
    sample = """
[items]
dict_config = {f"key_{x}" = x * 2 for x in [1, 2, 3]}
"""
    data = round_trip_loads(sample)
    assert data["items"]["dict_config"] == '{f"key_{x}" = x * 2 for x in [1, 2, 3]}'

    data["items"]["dict_config"].original = '{f"item_{x}" = x * 3 for x in [5, 10, 15]}'
    print("[DEBUG]:")
    print(data)

    resolved_config = resolve(data)
    print("[DEBUG]:")
    print(resolved_config)
    assert resolved_config["items"]["dict_config"] == {"item_5": 15, "item_10": 30, "item_15": 45}

    out = round_trip_dumps(data)
    rendered_data = render(out)
    assert rendered_data["items"]["dict_config"] == {"item_5": 15, "item_10": 30, "item_15": 45}

@pytest.mark.spec
@pytest.mark.mep0011
# @pytest.mark.xfail(reason="Arithmetic operations in expressions not implemented")
def test_folded_arithmetic_operations():
    sample = """
[calc]
result = <( 3 + 4 )>
"""
    data = round_trip_loads(sample)
    assert data["calc"]["result"] == '<( 3 + 4 )>'

    resolved_config = resolve(data)
    print("[DEBUG]:")
    print(resolved_config)
    assert resolved_config["calc"]["result"] == 7

    out = round_trip_dumps(data)
    rendered_data = render(out)
    assert rendered_data["calc"]["result"] == 7

# Test 11: Conditional Logic in Expressions
@pytest.mark.spec
@pytest.mark.mep0011
# @pytest.mark.xfail(reason="Conditional logic evaluation not implemented")
def test_fstring_conditional_logic():
    sample = """
[cond]
status = f"{'Yes' if true else 'No'}"
"""
    data = round_trip_loads(sample)
    assert data["cond"]["status"] == '''f"{'Yes' if true else 'No'}"'''

    resolved_config = resolve(data)
    print("[DEBUG]:")
    print(resolved_config)
    assert resolved_config["cond"]["status"] == "Yes"

    out = round_trip_dumps(data)
    rendered_data = render(out)
    assert rendered_data["cond"]["status"] == "Yes"


# @pytest.mark.spec
# @pytest.mark.mep0011
# # @pytest.mark.xfail(reason="Conditional logic evaluation not implemented")
# def test_deferred_conditional_logic():
#     sample = """[cond]
# status = <{ 'Yes' if true else 'No' }>"""
#     data = round_trip_loads(sample)
#     print("[DEBUG]:")
#     print(f"{data["cond"]["status"]}")
#     assert data["cond"]["status"] == "<{ 'Yes' if true else 'No' }>"
#     out = round_trip_dumps(data)
#     assert sample == out
#     rendered_data = render(out)
#     print(f"{rendered_data["cond"]["status"]}")
#     assert rendered_data["cond"]["status"] == "Yes"


@pytest.mark.spec
@pytest.mark.mep0011
# @pytest.mark.xfail(reason="Conditional logic evaluation not implemented")
def test_conditional_logic():
    sample = """[cond]
status = <('Yes' if true else 'No')>"""
    data = round_trip_loads(sample)
    assert data["cond"]["status"] == "<('Yes' if true else 'No')>"

    resolved_config = resolve(data)
    print("[DEBUG]:")
    print(resolved_config)
    assert resolved_config["cond"]["status"] == "Yes"

    out = round_trip_dumps(data)
    rendered_data = render(out)
    assert rendered_data["cond"]["status"] == "Yes"

# Is this really a type inference test? 
@pytest.mark.spec
@pytest.mark.mep0011
# @pytest.mark.xfail(reason="Inference in expressions not fully implemented")
def test_infer_expressions():
    """
    Ensures expressions (wrapped with <{ ... )>) are type-inferred from their result.
    """
    source = '''
    [exprs]
    # Arithmetic expression
    sum_val = <( 10 + 5 )>
    # String concatenation
    greeting = <( "Hello, " + "World!" )>
    # Boolean logic
    combo = <( true and false )>
    '''
    data = round_trip_loads(source)
    resolved_config = resolve(data)
    print("[DEBUG]:")
    print(resolved_config)


    exprs = resolved_config["exprs"]
    assert isinstance(exprs["sum_val"], int)
    assert exprs["sum_val"] == 15
    assert isinstance(exprs["greeting"], str)
    assert exprs["greeting"] == "Hello, World!"
    assert isinstance(exprs["combo"], bool)
    assert exprs["combo"] is False