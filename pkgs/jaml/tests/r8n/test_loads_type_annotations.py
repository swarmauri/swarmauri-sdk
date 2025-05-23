import pytest
from jaml import loads


@pytest.mark.unit
def test_loads_string_annotation():
    # Test a simple string with a type annotation.
    jml = """
[section]
greeting: str = "Hello, World!"
    """.strip()
    data = loads(jml)
    assert data["section"]["greeting"] == "Hello, World!"


@pytest.mark.unit
def test_loads_integer_annotation():
    # Test an integer with a type annotation.
    jml = """
[section]
answer: int = 42
    """.strip()
    data = loads(jml)
    assert data["section"]["answer"] == 42


@pytest.mark.unit
def test_loads_float_annotation():
    # Test a float with a type annotation.
    jml = """
[section]
pi: float = 3.14
    """.strip()
    data = loads(jml)
    assert abs(data["section"]["pi"] - 3.14) < 1e-6


@pytest.mark.unit
def test_loads_boolean_true_annotation():
    # Test a boolean true value with a type annotation.
    jml = """
[section]
is_active: bool = true
    """.strip()
    data = loads(jml)
    assert data["section"]["is_active"] is True


@pytest.mark.unit
def test_loads_boolean_false_annotation():
    # Test a boolean false value with a type annotation.
    jml = """
[section]
is_valid: bool = false
    """.strip()
    data = loads(jml)
    assert data["section"]["is_valid"] is False


@pytest.mark.unit
def test_loads_list_annotation():
    # Test a list with a type annotation.
    jml = """
[section]
colors: list = ["red", "green", "blue"]
    """.strip()
    data = loads(jml)
    assert data["section"]["colors"] == ["red", "green", "blue"]


@pytest.mark.unit
def test_loads_inline_table_annotation():
    # Test an inline table with a type annotation.
    # Note: In our current implementation, inline tables are returned as raw strings.
    jml = """
[section]
point: table = { x = 10, y = 20 }
    """.strip()
    data = loads(jml)
    point_dict = data["section"]["point"]
    assert isinstance(point_dict, dict)
    assert point_dict["x"] == 10
    assert point_dict["y"] == 20


@pytest.mark.unit
def test_loads_null_annotation():
    # Test a null value with a type annotation.
    jml = """
[section]
missing: null = null
    """.strip()
    data = loads(jml)
    assert data["section"]["missing"] is None
