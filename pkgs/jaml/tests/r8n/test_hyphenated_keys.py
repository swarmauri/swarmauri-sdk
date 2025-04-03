import pytest
from jaml import round_trip_loads, round_trip_dumps, loads, ScalarNode

PAYLOAD = '''
[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
'''.strip()

def test_round_trip_hyphenated_keys():
    """
    Test that round_trip_loads and round_trip_dumps correctly parse
    hyphenated section names and key names.
    """
    # Parse using round_trip_loads to get an AST preserving formatting.
    ast = round_trip_loads(PAYLOAD)
    
    # Verify that the section 'build-system' exists.
    section = next((sec for sec in ast.sections if sec.name == "build-system"), None)
    assert section is not None, "Section 'build-system' not found in AST."
    
    # Verify the 'requires' key exists and is parsed as a list with the expected value.
    requires_kv = next((kv for kv in section.keyvalues if kv.key == "requires"), None)
    assert requires_kv is not None, "Key 'requires' not found in section 'build-system'."
    assert requires_kv.type_annotation == "list", "The type of 'requires' should be 'list'."
    requires_list = [item.value for item in requires_kv.value.items if isinstance(item, ScalarNode)]
    expected_requires = ["poetry-core>=1.0.0"]
    assert requires_list == expected_requires, f"Expected requires {expected_requires}, got {requires_list}."
    
    # Verify that the hyphenated key 'build-backend' exists and has the expected string value.
    backend_kv = next((kv for kv in section.keyvalues if kv.key == "build-backend"), None)
    assert backend_kv is not None, "Key 'build-backend' not found in section 'build-system'."
    assert backend_kv.type_annotation == "str", "The type of 'build-backend' should be 'str'."
    backend_value = backend_kv.value.value if hasattr(backend_kv.value, "value") else backend_kv.value
    expected_backend = "poetry.core.masonry.api"
    assert backend_value == expected_backend, f"Expected build-backend '{expected_backend}', got '{backend_value}'."

def test_plain_loads_hyphenated_keys():
    """
    Test that loads() correctly converts a JML payload with hyphenated keys
    into the expected plain Python dict.
    """
    plain_data = loads(PAYLOAD)
    
    # Check that the plain data contains the 'build-system' section.
    assert "build-system" in plain_data, "Section 'build-system' not found in plain data."
    section_data = plain_data["build-system"]
    
    # Verify that the 'requires' key is present and parsed correctly.
    assert "requires" in section_data, "Key 'requires' not found in plain data for section 'build-system'."
    expected_requires = ["poetry-core>=1.0.0"]
    assert section_data["requires"] == expected_requires, (
        f"Expected requires {expected_requires}, got {section_data['requires']}."
    )
    
    # Verify that the hyphenated key 'build-backend' is present and has the expected value.
    assert "build-backend" in section_data, "Key 'build-backend' not found in plain data for section 'build-system'."
    expected_backend = "poetry.core.masonry.api"
    assert section_data["build-backend"] == expected_backend, (
        f"Expected build-backend {expected_backend}, got {section_data['build-backend']}."
    )
