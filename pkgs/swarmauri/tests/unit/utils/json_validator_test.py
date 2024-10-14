import pytest
from swarmauri.utils.json_validator import load_json_file, validate_json
import json
import tempfile
import os


@pytest.mark.unit
def test_load_json_file():
    test_data = {"key": "value", "number": 42}

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        json.dump(test_data, temp_file)
        temp_file_path = temp_file.name

    try:
        loaded_data = load_json_file(temp_file_path)
        assert loaded_data == test_data
    finally:
        os.unlink(temp_file_path)


@pytest.mark.unit
def test_load_json_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_json_file("non_existent_file.json")


@pytest.mark.unit
def test_validate_json_valid():
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer", "minimum": 0},
        },
        "required": ["name", "age"],
    }

    valid_data = {"name": "John Doe", "age": 30}

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        json.dump(schema, temp_file)
        schema_file_path = temp_file.name

    try:
        assert validate_json(valid_data, schema_file_path) == True
    finally:
        os.unlink(schema_file_path)


@pytest.mark.unit
def test_validate_json_invalid():
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer", "minimum": 0},
        },
        "required": ["name", "age"],
    }

    invalid_data = {"name": "John Doe", "age": "thirty"}  # age should be an integer

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        json.dump(schema, temp_file)
        schema_file_path = temp_file.name

    try:
        assert validate_json(invalid_data, schema_file_path) == False
    finally:
        os.unlink(schema_file_path)


@pytest.mark.unit
def test_validate_json_schema_not_found():
    with pytest.raises(FileNotFoundError):
        validate_json({"key": "value"}, "non_existent_schema.json")
