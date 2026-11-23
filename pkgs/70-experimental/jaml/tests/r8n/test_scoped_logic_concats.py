from jaml import render  # Adjust the import if your module path differs.


def test_concat_single_global_variable():
    """
    Test concatenation with a single global variable.
    """
    jml = """
[logic]
greeting: str = ~( "Hello, " + $user.name )
    """.strip()
    context = {"user": {"name": "Alice"}}
    rendered_jml = render(jml, context)
    expected = 'greeting: str = "Hello, Alice"'
    assert expected in rendered_jml


def test_concat_multiple_global_variables():
    """
    Test concatenation with multiple global variables (string and int).
    """
    jml = """
[logic]
summary: str = ~( "User: " + $user.name + ", Age: " + $user.age )
    """.strip()
    context = {"user": {"name": "Bob", "age": 42}}
    rendered_jml = render(jml, context)
    expected = 'summary: str = "User: Bob, Age: 42"'
    assert expected in rendered_jml


def test_concat_non_string_types():
    """
    Test concatenation with non-string types that require conversion.
    """
    jml = """
[logic]
mix: str = ~( "Value: " + $value + ", Status: " + $status )
    """.strip()
    context = {"value": 100, "status": "active"}
    rendered_jml = render(jml, context)
    expected = 'mix: str = "Value: 100, Status: active"'
    assert expected in rendered_jml


def test_concat_several_short_globals():
    """
    Test concatenation of several short global variables.
    """
    jml = """
[logic]
concat: str = ~( $a + $b + $c )
    """.strip()
    context = {"a": "X", "b": "Y", "c": "Z"}
    rendered_jml = render(jml, context)
    expected = 'concat: str = "XYZ"'
    assert expected in rendered_jml


def test_concat_mixed_types():
    """
    Test concatenation with mixed types (float and bool).
    """
    jml = """
[logic]
complex: str = ~( "Result: " + $x + " & " + $y )
    """.strip()
    context = {"x": 3.14, "y": True}
    rendered_jml = render(jml, context)
    expected = 'complex: str = "Result: 3.14 & True"'
    assert expected in rendered_jml
