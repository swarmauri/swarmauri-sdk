# swarmauri/standard/utils/json_validator.py
import json
import jsonschema
from jsonschema import validate

def load_json_file(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        return json.load(file)

def validate_json(data: dict, schema_file: str) -> bool:
    schema = load_json_file(schema_file)
    try:
        validate(instance=data, schema=schema)
    except jsonschema.exceptions.ValidationError as err:
        print(f"JSON validation error: {err.message}")
        return False
    return True