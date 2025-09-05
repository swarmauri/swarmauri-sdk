import pytest
from jaml import loads, round_trip_loads


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

    data["config"]["url"] = 'f"@{alt}/config.toml"'
    print("[DEBUG]:")
    print(data)

    resolved_config = data.resolve()
    print("[DEBUG]:")
    print(resolved_config)
    assert resolved_config["config"]["url"] == "/home/alt/config.toml"

    data.dumps()
    rendered_data = data.render()
    print("[DEBUG]:")
    print(rendered_data)
    assert rendered_data["config"]["url"] == "/home/alt/config.toml"


@pytest.mark.spec
@pytest.mark.mep0011
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

    data["config"]["url"] = 'f"@{paths.alt}/config.toml"'
    print("[DEBUG]:")
    print(data)

    resolved_config = data.resolve()  # Use instance method
    print("[DEBUG]:")
    print(resolved_config)
    assert resolved_config["config"]["url"] == "/home/alt/config.toml"


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

    data["user"]["greeting"] = 'f"Hello, %{altname}!"'
    print("[DEBUG]:")
    print(data)

    resolved_config = data.resolve()  # Use instance method
    print("[DEBUG]:")
    print(resolved_config)
    assert resolved_config["user"]["greeting"] == "Hello, Bob!"

    data.dumps()
    rendered_data = data.render()
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

    resolved_config = data.resolve()
    print("[DEBUG]:")
    print(resolved_config)
    assert (
        resolved_config["logic"]["summary"] == 'f"User: ${user.name}, Age: ${user.age}"'
    )

    data.dumps()
    rendered_data = data.render(context={"user": {"name": "Alice", "age": 30}})
    assert rendered_data["logic"]["summary"] == "User: Alice, Age: 30"


# Test 5: F-String Interpolation
@pytest.mark.spec
@pytest.mark.mep0011
# @pytest.mark.xfail(reason="F-string interpolation evaluation not fully implemented.")
def test_context_f_string():
    sample = """
[message]
text = f"Hello, ${name}!"
"""
    # Assuming 'name' is provided via render context.
    data = round_trip_loads(sample)
    out = data.dumps()

    resolved_config = data.resolve()
    print("[DEBUG]:")
    print(resolved_config)
    assert resolved_config["message"]["text"] == 'f"Hello, ${name}!"'

    rendered_data = data.render(context={"name": "Alice"})
    assert rendered_data["message"]["text"] == "Hello, Alice!"

    data_again = loads(out)
    assert data_again["message"]["text"] == 'f"Hello, ${name}!"'


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
    assert (
        data["api"]["endpoint"]
        == '<( "http://" + @{server.host} + ":" + @{server.port} + "/api?token=" + ${auth_token} )>'
    )

    data.resolve()
    print("[DEBUG]:")
    print(data)
    assert (
        data["api"]["endpoint"] == 'f"http://prodserver:8080/api?token=${auth_token}"'
    )

    print("[DEBUG SETTER]: START")
    data["api"]["endpoint"] = (
        '<( "http://" + @{server.devhost} + ":" + @{server.port} + "/api?token=" + ${auth_token} )>'
    )
    data.resolve()
    print("[DEBUG SETTER]:")
    print(data)

    data.dumps()
    rendered_data = data.render(context={"auth_token": "ABC123"})
    print("[DEBUG]:")
    print(rendered_data)
    assert rendered_data["api"]["endpoint"] == "http://devserver:8080/api?token=ABC123"


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

    data["items"]["list_config"] = '[f"item_{x}" for x in [5, 10, 15]]'
    print("[DEBUG]:")
    print(data)

    resolved_config = data.resolve()
    print("[DEBUG]:")
    print(resolved_config)
    assert resolved_config["items"]["list_config"] == ["item_5", "item_10", "item_15"]

    data.dumps()
    rendered_data = data.render()
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
    assert data["items"]["dict_config"] == '{f"key_{x}" : x*2 for x in [1, 2, 3]}'

    data["items"]["dict_config"] = '{f"item_{x}": x * 3 for x in [5, 10, 15]}'
    print("[DEBUG]:")
    print(data)

    resolved_config = data.resolve()
    print("[DEBUG]:")
    print(resolved_config)
    assert resolved_config["items"]["dict_config"] == {
        "item_5": 15,
        "item_10": 30,
        "item_15": 45,
    }

    data.dumps()
    rendered_data = data.render()
    print("[DEBUG]:")
    print(rendered_data)
    assert rendered_data["items"]["dict_config"] == {
        "item_5": 15,
        "item_10": 30,
        "item_15": 45,
    }


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
    assert data["items"]["dict_config"] == '{f"key_{x}" = x*2 for x in [1, 2, 3]}'

    data["items"]["dict_config"] = '{f"item_{x}" = x * 3 for x in [5, 10, 15]}'
    print("[DEBUG]:")
    print(data)

    resolved_config = data.resolve()
    print("[DEBUG]:")
    print(resolved_config)
    assert resolved_config["items"]["dict_config"] == {
        "item_5": 15,
        "item_10": 30,
        "item_15": 45,
    }

    data.dumps()
    rendered_data = data.render()
    assert rendered_data["items"]["dict_config"] == {
        "item_5": 15,
        "item_10": 30,
        "item_15": 45,
    }


@pytest.mark.spec
@pytest.mark.mep0011
# @pytest.mark.xfail(reason="Arithmetic operations in expressions not implemented")
def test_folded_arithmetic_operations():
    sample = """
[calc]
result = <( 3 + 4 )>
"""
    data = round_trip_loads(sample)
    print("[DEBUG]:")
    print(data)
    assert data["calc"]["result"] == "<( 3 + 4 )>"

    data["calc"]["result"] = "<( 7 + 4 )>"
    print("[DEBUG]:")
    print(data)

    resolved_config = data.resolve()
    print("[DEBUG]:")
    print(data)
    assert resolved_config["calc"]["result"] == 11

    data.dumps()
    rendered_data = data.render()
    assert rendered_data["calc"]["result"] == 11


@pytest.mark.spec
@pytest.mark.mep0011
# @pytest.mark.xfail(reason="expression evaluation not implemented")
def test_string_and_arithmetic_expressions():
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

[calc]
result = <( 3 + 4 )>
"""
    # Provide context for the deferred part.
    data = round_trip_loads(sample)
    print("[DEBUG]:")
    print(data)
    assert (
        data["api"]["endpoint"]
        == '<( "http://" + @{server.host} + ":" + @{server.port} + "/api?token=" + ${auth_token} )>'
    )
    assert data["calc"]["result"] == "<( 3 + 4 )>"

    data["api"]["endpoint"] = (
        '<( "http://" + @{server.devhost} + ":" + @{server.port} + "/api?token=" + ${auth_token} )>'
    )
    data["calc"]["result"] = "<( 7 + 4 )>"
    print("[DEBUG]:")
    print(data)

    resolved_config = data.resolve()
    print("[DEBUG]:")
    print(resolved_config)
    assert (
        resolved_config["api"]["endpoint"]
        == 'f"http://devserver:8080/api?token=${auth_token}"'
    )
    assert resolved_config["calc"]["result"] == 11

    data.dumps()
    rendered_data = data.render(context={"auth_token": "ABC123"})
    print("[DEBUG]:")
    print(rendered_data)
    assert rendered_data["api"]["endpoint"] == "http://devserver:8080/api?token=ABC123"
    assert rendered_data["calc"]["result"] == 11


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
    print("[DEBUG]:")
    print(data)
    assert data["cond"]["status"] == '''f"{'Yes' if true else 'No'}"'''

    data["cond"]["status"] = '''f"{'Yes' if false else 'No'}"'''
    print("[DEBUG]:")
    print(data)

    resolved_config = data.resolve()
    print("[DEBUG]:")
    print(resolved_config)
    assert resolved_config["cond"]["status"] == "No"

    data.dumps()
    rendered_data = data.render()
    print("[DEBUG]:")
    print(rendered_data)
    assert rendered_data["cond"]["status"] == "No"


@pytest.mark.spec
@pytest.mark.mep0011
# @pytest.mark.xfail(reason="Conditional logic evaluation not implemented")
def test_conditional_logic():
    sample = """[cond]
status = <('Yes' if true else 'No')>"""
    data = round_trip_loads(sample)
    print("[DEBUG]:")
    print(data)
    assert data["cond"]["status"] == "<( 'Yes' if true else 'No' )>"

    data["cond"]["status"] = "<('Yes' if false else 'No')>"
    print("[DEBUG]:")
    print(data)

    resolved_config = data.resolve()
    print("[DEBUG]:")
    print(resolved_config)
    assert resolved_config["cond"]["status"] == "No"

    data.dumps()
    rendered_data = data.render()
    print("[DEBUG]:")
    print(rendered_data)
    assert rendered_data["cond"]["status"] == "No"


# Is this really a type inference test?
@pytest.mark.spec
@pytest.mark.mep0011
# @pytest.mark.xfail(reason="Inference in expressions not fully implemented")
def test_infer_expressions():
    """
    Ensures expressions (wrapped with <{ ... )>) are type-inferred from their result.
    """
    source = """
    [exprs]
    # Arithmetic expression
    sum_val = <( 10 + 5 )>
    # String concatenation
    greeting = <( "Hello, " + "World!" )>
    # Boolean logic
    combo = <( true and false )>
    """
    data = round_trip_loads(source)
    resolved_config = data.resolve()
    print("[DEBUG]:")
    print(resolved_config)

    exprs = resolved_config["exprs"]
    assert isinstance(exprs["sum_val"], int)
    assert exprs["sum_val"] == 15
    assert isinstance(exprs["greeting"], str)
    assert exprs["greeting"] == "Hello, World!"
    assert isinstance(exprs["combo"], bool)
    assert exprs["combo"] is False
