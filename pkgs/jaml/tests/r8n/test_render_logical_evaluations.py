import pytest
from jaml import render, loads


@pytest.mark.unit
def test_rt_ren_logical_string_true():
    jml = """
[logic]
status: str = ~( "Active" if true else "Inactive" )
    """.strip()
    rendered_output = render(jml)
    data = loads(rendered_output)
    assert data["logic"]["status"] == "Active"


@pytest.mark.unit
def test_rt_ren_logical_string_false():
    jml = """
[logic]
status: str = ~( "Active" if false else "Inactive" )
    """.strip()
    rendered_output = render(jml)
    data = loads(rendered_output)
    assert data["logic"]["status"] == "Inactive"


@pytest.mark.unit
def test_rt_ren_logical_integer():
    jml = """
[logic]
number: int = ~( 100 if true else 0 )
    """.strip()
    rendered_output = render(jml)
    data = loads(rendered_output)
    assert data["logic"]["number"] == 100


@pytest.mark.unit
def test_rt_ren_logical_boolean():
    jml = """
[logic]
flag: bool = ~( true if false else false )
    """.strip()
    rendered_output = render(jml)
    data = loads(rendered_output)
    assert data["logic"]["flag"] is False


@pytest.mark.unit
def test_rt_ren_logical_list_comprehension():
    jml = """
[logic]
values: list = ~( [x * 2 for x in [1, 2, 3]] )
    """.strip()
    rendered_output = render(jml)
    data = loads(rendered_output)
    assert data["logic"]["values"] == [2, 4, 6]


@pytest.mark.unit
def test_rt_ren_nested_logical_with_context():
    jml = """
[logic]
message: str = ~( "Hello, Admin" if $user.role == "admin" else "Hello, User" )
    """.strip()
    context = {"user": {"role": "admin"}}
    rendered_output = render(jml, context=context)
    data = loads(rendered_output)
    assert data["logic"]["message"] == "Hello, Admin"


@pytest.mark.unit
def test_rt_ren_complex_nested_logical():
    jml = """
[logic]
access: str = ~( "Full" if true else ("Partial" if false else "None") )
    """.strip()
    rendered_output = render(jml)
    data = loads(rendered_output)
    assert data["logic"]["access"] == "Full"


@pytest.mark.unit
def test_rt_ren_nested_logical_with_context_percent_marker():
    # This test uses the % marker to resolve external context.
    jml = """
[logic]
message: str = ~( "Hello, Admin" if $user.role == "admin" else "Hello, User" )
    """.strip()
    context = {"user": {"role": "admin"}}
    rendered_output = render(jml, context=context)
    data = loads(rendered_output)
    assert data["logic"]["message"] == "Hello, Admin"


@pytest.mark.unit
def test_rt_ren_nested_logical_with_at_marker():
    # This test uses the @ marker to resolve a value from another section in the same JML document.
    jml = """
[user]
role: str = "admin"

[logic]
message: str = ~( "Hello, Admin" if @user.role == "admin" else "Hello, User" )
    """.strip()
    rendered_output = render(jml)
    data = loads(rendered_output)
    assert data["logic"]["message"] == "Hello, Admin"
