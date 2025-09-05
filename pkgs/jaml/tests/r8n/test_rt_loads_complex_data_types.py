import pytest
from jaml import round_trip_loads, loads


@pytest.mark.unit
def test_rt_loads_inline_array():
    jml = """
[section]
numbers = [1, 2, 3, 4]
    """.strip()
    ast = round_trip_loads(jml)
    dumped_str = ast.to_jml()
    data = loads(dumped_str)
    assert data["section"]["numbers"] == [1, 2, 3, 4]


@pytest.mark.unit
def test_rt_loads_multiline_array():
    jml = """
[section]
colors = ["red", "green", "blue"]
    """.strip()
    ast = round_trip_loads(jml)
    dumped_str = ast.to_jml()
    data = loads(dumped_str)
    assert data["section"]["colors"] == ["red", "green", "blue"]


@pytest.mark.unit
def test_rt_loads_dynamic_list():
    jml = """
[section]
active_users = ~[f"User: {user}" for user in ["Alice", "Bob"]]
    """.strip()
    ast = round_trip_loads(jml)
    dumped_str = ast.to_jml()
    data = loads(dumped_str)
    assert (
        data["section"]["active_users"]
        == """~[f"User: {user}" for user in ["Alice", "Bob"]]"""
    )


@pytest.mark.unit
def test_rt_loads_inline_table():
    jml = """
[section]
point = { x = 10, y = 20 }
    """.strip()
    ast = round_trip_loads(jml)
    dumped_str = ast.to_jml()
    data = loads(dumped_str)
    assert data["section"]["point"] == {"x": 10, "y": 20}


@pytest.mark.unit
def test_rt_loads_nested_inline_table():
    jml = """
[section]
user = { name = "Azzy", details = { age = 9, role = "admin" } }
    """.strip()
    ast = round_trip_loads(jml)
    dumped_str = ast.to_jml()
    data = loads(dumped_str)
    assert data["section"]["user"]["name"] == "Azzy"
    assert data["section"]["user"]["details"] == {"age": 9, "role": "admin"}


@pytest.mark.unit
def test_rt_loads_multiline_table():
    jml = """
[address]
city = "New York"
zip = 10001
    """.strip()
    ast = round_trip_loads(jml)
    dumped_str = ast.to_jml()
    data = loads(dumped_str)
    assert data["address"]["city"] == "New York"
    assert data["address"]["zip"] == 10001


@pytest.mark.unit
def test_rt_loads_dynamic_structure():
    jml = """
[section]
dynamic_value = ~(42 if true else 0)
    """.strip()
    ast = round_trip_loads(jml)
    dumped_str = ast.to_jml()
    data = loads(dumped_str)
    assert data["section"]["dynamic_value"] == "~(42 if true else 0)"
