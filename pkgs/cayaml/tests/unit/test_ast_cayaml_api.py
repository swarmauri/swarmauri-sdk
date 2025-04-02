import io
import pytest

from cayaml import round_trip_load, round_trip_loads, round_trip_dump, round_trip_dumps


def test_round_trip_loads_scalars():
    yaml_str = """
    # Testing scalars
    integer: 42
    float_val: 3.14
    boolean_true: true
    boolean_false: false
    none_val: null
    string_val_quoted: "hello"
    string_val_unquoted: world
    """
    data = round_trip_loads(yaml_str)
    assert data["integer"] == 42
    assert data["float_val"] == 3.14
    assert data["boolean_true"] is True
    assert data["boolean_false"] is False
    assert data["none_val"] is None
    assert data["string_val_quoted"] == "hello"
    assert data["string_val_unquoted"] == "world"


def test_round_trip_loads_list():
    yaml_str = """
    - 1
    - 2
    - 3
    """
    data = round_trip_loads(yaml_str)
    assert data == [1, 2, 3]


def test_round_trip_loads_nested():
    yaml_str = """
    parent:
      child_list:
        - item1
        - item2
      child_map:
        subkey1: subval1
        subkey2: subval2
    """
    data = round_trip_loads(yaml_str)

    assert data["parent"]["child_list"] == ["item1", "item2"]
    assert data["parent"]["child_map"]["subkey1"] == "subval1"
    assert data["parent"]["child_map"]["subkey2"] == "subval2"


def test_round_trip_dumps_scalars():
    data = {
        "integer": 42,
        "float_val": 3.14,
        "boolean_true": True,
        "boolean_false": False,
        "none_val": None,
        "string_val": "hello world",
    }
    yaml_str = round_trip_dumps(data)
    # Simple sanity checks
    assert "integer: 42" in yaml_str
    assert "float_val: 3.14" in yaml_str
    assert "boolean_true: true" in yaml_str
    assert "boolean_false: false" in yaml_str
    # The "null" string is used for None
    assert "none_val: null" in yaml_str


def test_round_trip_dumps_list():
    data = [1, 2, 3, "four"]
    yaml_str = round_trip_dumps(data)

    # Each item should be on its own line with a '- ' prefix or '-\n' block
    lines = yaml_str.splitlines()
    assert lines[0] == "- 1"
    assert lines[1] == "- 2"
    assert lines[2] == "- 3"
    assert lines[3] == "- four"


def test_round_trip_dumps_get_attribute_from_list():
    data = [1, 2, 3, "four"]
    yaml_str = round_trip_dumps(data)

    # Each item should be on its own line with a '- ' prefix or '-\n' block
    lines = yaml_str.splitlines()
    value = lines[0]
    assert type(value) is str


def test_round_trip():
    yaml_str = """
    top_level: hello
    numeric: 123
    list_stuff:
      - alpha
      - beta
      - gamma
    nested:
      key1: val1
      key2: val2
    """
    original_data = round_trip_loads(yaml_str)
    round_trip_dumped = round_trip_dumps(original_data)
    data_after_round_trip = round_trip_loads(round_trip_dumped)
    assert data_after_round_trip == original_data


def test_round_trip_load_round_trip_dump_file_object():
    input_str = """
    key1: val1
    key2: val2
    key3:
      - list_item1
      - list_item2
    """
    # Simulate reading from a file
    file_in = io.StringIO(input_str)
    data = round_trip_load(file_in)
    assert data["key1"] == "val1"
    assert data["key2"] == "val2"
    assert data["key3"] == ["list_item1", "list_item2"]

    # Simulate writing to a file
    file_out = io.StringIO()
    round_trip_dump(data, file_out)
    file_out.seek(0)  # Go back to the beginning
    output_str = file_out.read()
    # Round-trip test from the output
    data2 = round_trip_loads(output_str)
    assert data2 == data


if __name__ == "__main__":
    pytest.main([__file__])
