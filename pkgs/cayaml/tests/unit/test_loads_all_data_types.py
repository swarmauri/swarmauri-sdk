import math
import pytest
from cayaml import loads


@pytest.mark.unit
def test_strings():
    yaml_str = """
    plain_str: hello
    quoted_str: "hello world"
    """
    data = loads(yaml_str)
    assert data["plain_str"] == "hello"
    assert data["quoted_str"] == "hello world"


@pytest.mark.unit
def test_booleans():
    yaml_str = """
    bool_true: true
    bool_false: false
    """
    data = loads(yaml_str)
    assert data["bool_true"] is True
    assert data["bool_false"] is False


@pytest.mark.unit
def test_null():
    yaml_str = """
    null_val: null
    """
    data = loads(yaml_str)
    assert data["null_val"] is None


@pytest.mark.unit
def test_integers():
    yaml_str = """
    decimal_val: 42
    hex_val: 0x2A
    oct_val: 0o52
    bin_val: 0b101010
    """
    data = loads(yaml_str)
    assert data["decimal_val"] == 42
    assert data["hex_val"] == 42
    assert data["oct_val"] == 42
    assert data["bin_val"] == 42


@pytest.mark.unit
def test_floats():
    yaml_str = """
    float_val: 3.14
    inf_val: .inf
    neg_inf_val: -.inf
    nan_val: .nan
    """
    data = loads(yaml_str)
    assert data["float_val"] == 3.14
    assert math.isinf(data["inf_val"]) and data["inf_val"] > 0
    assert math.isinf(data["neg_inf_val"]) and data["neg_inf_val"] < 0
    assert math.isnan(data["nan_val"])


@pytest.mark.unit
def test_sequence():
    yaml_str = """
    my_list:
      - item1
      - item2
      - item3
    """
    data = loads(yaml_str)
    assert data["my_list"] == ["item1", "item2", "item3"]


@pytest.mark.unit
def test_mapping():
    yaml_str = """
    my_map:
      nested: stuff
      more_nested:
        - 1
        - 2
    """
    data = loads(yaml_str)
    assert data["my_map"]["nested"] == "stuff"
    assert data["my_map"]["more_nested"] == [1, 2]
