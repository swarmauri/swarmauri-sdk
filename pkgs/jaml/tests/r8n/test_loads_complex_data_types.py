import pytest
from jaml import loads


@pytest.mark.unit
def test_loads_inline_array():
    # Test a simple inline array.
    jml = """
[section]
numbers = [1, 2, 3, 4]
    """.strip()
    data = loads(jml)
    assert data["section"]["numbers"] == [1, 2, 3, 4]


@pytest.mark.unit
def test_loads_multiline_array():
    # Test a multiline array formatted on one line.
    jml = """
[section]
colors = ["red", "green", "blue"]
    """.strip()
    data = loads(jml)
    assert data["section"]["colors"] == ["red", "green", "blue"]


@pytest.mark.unit
def test_loads_dynamic_list():
    # Test a dynamic list created with a list comprehension.
    # The tilde (~) indicates that the expression should be evaluated.
    jml = """
[section]
active_users = ~[f"User: {user}" for user in ["Alice", "Bob"]]
    """.strip()
    data = loads(jml)
    assert (
        data["section"]["active_users"]
        == '~[f"User: {user}" for user in ["Alice", "Bob"]]'
    )


@pytest.mark.unit
def test_loads_inline_table():
    # Test an inline table (dictionary-like structure).
    jml = """
[section]
point = { x = 10, y = 20 }
    """.strip()
    data = loads(jml)
    # Expect the inline table to be parsed into a dict.
    assert data["section"]["point"] == {"x": 10, "y": 20}


@pytest.mark.unit
def test_loads_nested_inline_table():
    # Test an inline table that contains a nested inline table.
    jml = """
[section]
user: table = { name = "Azzy", details = { age = 9, role = "admin" } }
    """.strip()
    data = loads(jml)
    assert data["section"]["user"]["name"] == "Azzy"
    assert data["section"]["user"]["details"] == {"age": 9, "role": "admin"}


@pytest.mark.unit
def test_loads_multiline_table():
    # Test a standard multiline table (a section with multiple key-value pairs).
    jml = """
[address]
city = "New York"
zip = 10001
    """.strip()
    data = loads(jml)
    assert data["address"]["city"] == "New York"
    assert data["address"]["zip"] == 10001


@pytest.mark.unit
def test_loads_dynamic_structure():
    # Test a dynamic inline expression within a key's value.
    # The expression is encapsulated in parentheses and prefixed with '~'.
    jml = """
[section]
dynamic_value = ~(42 if true else 0)
    """.strip()
    data = loads(jml)
    assert data["section"]["dynamic_value"] == "~(42 if true else 0)"
