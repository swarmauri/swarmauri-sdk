import pytest
from jaml import render


@pytest.mark.unit
def test_render_global_scope_variable():
    """
    Test that render evaluates a global scope reference correctly with provided context.
    """
    jml = """
[logic]
greeting: str = ~( "Hello, " + $user.name )
    """.strip()
    context = {"user": {"name": "Alice"}}
    rendered_jml = render(jml, context)
    assert 'greeting: str = "Hello, Alice"' in rendered_jml


@pytest.mark.unit
def test_render_global_scope_list_reference():
    """
    Test that render evaluates a list index reference from global scope.
    """
    jml = """
[logic]
first_value: int = {^ ${values}[0] + 10 ^}
    """.strip()
    context = {"values": [5, 10, 15]}
    rendered_jml = render(jml, context)
    assert "first_value: int = 15" in rendered_jml


@pytest.mark.unit
def test_render_nested_global_scope():
    """
    Test that render evaluates nested global scope references.
    """
    jml = """
[logic]
full_name: str = ~( $user.profile.first + " " + $user.profile.last )
    """.strip()
    context = {"user": {"profile": {"first": "John", "last": "Doe"}}}
    rendered_jml = render(jml, context)
    assert 'full_name: str = "John Doe"' in rendered_jml


@pytest.mark.unit
def test_render_local_vs_global():
    """
    Test that render distinguishes between local and global references.
    """
    jml = """
[test]
name: str = "LocalName"
greeting: str = ~( "Hello, " + @name )
    """.strip()
    context = {
        "name": "GlobalName"  # Global context should be overridden by local 'name'
    }
    rendered_jml = render(jml, context)
    assert 'greeting: str = "Hello, LocalName"' in rendered_jml


@pytest.mark.unit
def test_render_multiple_global_scopes():
    """
    Test that render evaluates multiple global scope references in a single expression.
    """
    jml = """
[logic]
summary: str = ~( "User: " + $user.name + ", Age: " + $user.age )
    """.strip()
    context = {"user": {"name": "Alice", "age": "30"}}
    rendered_jml = render(jml, context)
    assert 'summary: str = "User: Alice, Age: 30"' in rendered_jml
