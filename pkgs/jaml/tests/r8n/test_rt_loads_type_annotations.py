import pytest
from jaml import round_trip_loads, round_trip_dumps, loads


@pytest.mark.unit
def test_rt_loads_string_annotation():
    # Test a simple string with a type annotation.
    jml = """
[section]
greeting: str = "Hello, World!"
    """.strip()
    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)
    assert data["section"]["greeting"] == "Hello, World!"


@pytest.mark.unit
def test_rt_loads_integer_annotation():
    # Test an integer with a type annotation.
    jml = """
[section]
answer: int = 42
    """.strip()
    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)
    assert data["section"]["answer"] == 42


@pytest.mark.unit
def test_rt_loads_float_annotation():
    # Test a float with a type annotation.
    jml = """
[section]
pi: float = 3.14
    """.strip()
    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)
    assert abs(data["section"]["pi"] - 3.14) < 1e-6


@pytest.mark.unit
def test_rt_loads_boolean_true_annotation():
    # Test a boolean true value with a type annotation.
    jml = """
[section]
is_active: bool = true
    """.strip()
    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)
    assert data["section"]["is_active"] is True


@pytest.mark.unit
def test_rt_loads_boolean_false_annotation():
    # Test a boolean false value with a type annotation.
    jml = """
[section]
is_valid: bool = false
    """.strip()
    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)
    assert data["section"]["is_valid"] is False


@pytest.mark.unit
def test_rt_loads_list_annotation():
    # Test a list with a type annotation.
    jml = """
[section]
colors: list = ["red", "green", "blue"]
    """.strip()
    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)
    assert data["section"]["colors"] == ["red", "green", "blue"]


@pytest.mark.unit
def test_rt_loads_inline_table_annotation():
    jml = """
[section]
point: table = { x = 10, y = 20 }
    """.strip()
    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)

    # Expect a dict, not a string
    point_dict = data["section"]["point"]
    assert isinstance(point_dict, dict)
    assert point_dict["x"] == 10
    assert point_dict["y"] == 20


@pytest.mark.unit
def test_rt_loads_null_annotation():
    # Test a null value with a type annotation.
    jml = """
[section]
missing: null = null
    """.strip()
    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)
    assert data["section"]["missing"] is None
