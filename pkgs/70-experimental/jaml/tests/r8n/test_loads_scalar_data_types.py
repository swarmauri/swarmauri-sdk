import math
import pytest
from jaml import loads


@pytest.mark.unit
def test_loads_string():
    # Test a simple string value.
    jml = """
[section]
greeting = "Hello, World!"
    """.strip()
    data = loads(jml)
    assert data["section"]["greeting"] == "Hello, World!"


@pytest.mark.unit
def test_loads_preserve_newlines():
    # Test a simple string value.
    jml = """
[section]
greeting = "Hello, World!\nHello, World!"
    """.strip()
    data = loads(jml)
    assert data["section"]["greeting"] == "Hello, World!\nHello, World!"


@pytest.mark.unit
def test_loads_literal_string():
    # Test a simple string value.
    jml = """
[paths]
windows_path = "C:\\Users\\Alice\\My Docs"
    """.strip()
    data = loads(jml)
    assert data["paths"]["windows_path"] == "C:\\Users\\Alice\\My Docs"


@pytest.mark.unit
def test_loads_integer():
    # Test an integer value.
    jml = """
[section]
answer = 42
    """.strip()
    data = loads(jml)
    assert data["section"]["answer"] == 42


@pytest.mark.unit
def test_loads_float():
    # Test a float value.
    jml = """
[section]
pi = 3.14
    """.strip()
    data = loads(jml)
    assert abs(data["section"]["pi"] - 3.14) < 1e-6


@pytest.mark.unit
def test_loads_special_float_inf():
    # Test special float value: infinity.
    jml = """
[section]
infinity = inf
    """.strip()
    data = loads(jml)
    assert data["section"]["infinity"] == float("inf")


@pytest.mark.unit
def test_loads_special_float_nan():
    # Test special float value: NaN.
    jml = """
[section]
not_a_number = nan
    """.strip()
    data = loads(jml)
    assert math.isnan(data["section"]["not_a_number"])


@pytest.mark.unit
def test_loads_boolean_true():
    # Test a boolean true value.
    jml = """
[section]
is_active = true
    """.strip()
    data = loads(jml)
    assert data["section"]["is_active"] is True


@pytest.mark.unit
def test_loads_boolean_false():
    # Test a boolean false value.
    jml = """
[section]
is_valid = false
    """.strip()
    data = loads(jml)
    assert data["section"]["is_valid"] is False


@pytest.mark.unit
def test_loads_null():
    # Test a null value.
    jml = """
[section]
missing = null
    """.strip()
    data = loads(jml)
    assert data["section"]["missing"] is None


@pytest.mark.unit
def test_loads_octal_integer():
    # Test an octal integer value.
    # Here, 0o52 in octal equals 42 in decimal.
    jml = """
[section]
octal = 0o52
    """.strip()
    data = loads(jml)
    assert data["section"]["octal"] == 42


@pytest.mark.unit
def test_loads_hexadecimal_integer():
    # Test a hexadecimal integer value.
    # 0x2A in hexadecimal equals 42 in decimal.
    jml = """
[section]
hex = 0x2A
    """.strip()
    data = loads(jml)
    assert data["section"]["hex"] == 42


@pytest.mark.unit
def test_loads_binary_integer():
    # Test a binary integer value.
    # 0b101010 in binary equals 42 in decimal.
    jml = """
[section]
binary = 0b101010
    """.strip()
    data = loads(jml)
    assert data["section"]["binary"] == 42
