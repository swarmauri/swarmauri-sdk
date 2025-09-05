"""Unit tests for ``YamlMixin`` utilities."""

import pytest
import yaml
from swarmauri_base.YamlMixin import YamlMixin


# --- Dummy model for testing ---
class DummyModel(YamlMixin):
    """Simple model used for YAML tests."""

    name: str
    age: int
    api_key: str = None


# --- Unit Tests ---


@pytest.mark.unit
def test_model_validate_yaml_success():
    """Validate successful YAML parsing."""
    yaml_data = """
    name: Alice
    age: 25
    api_key: secret_key
    """
    model = DummyModel.model_validate_yaml(yaml_data)
    assert model.name == "Alice"
    assert model.age == 25
    assert model.api_key == "secret_key"


@pytest.mark.unit
def test_model_validate_yaml_invalid_yaml():
    """Raise ``ValueError`` when YAML is malformed."""
    # Introduce a YAML formatting error (bad indentation)
    invalid_yaml = """
    name: Alice
      age: 25
    api_key: secret_key
    """
    with pytest.raises(ValueError, match="Invalid YAML data"):
        DummyModel.model_validate_yaml(invalid_yaml)


@pytest.mark.unit
def test_model_validate_yaml_validation_error():
    """Handle invalid field types during parsing."""
    # 'age' should be an int but provided as a string that cannot be converted
    yaml_data = """
    name: Bob
    age: not_a_number
    api_key: secret_key
    """
    with pytest.raises(ValueError, match="Validation failed"):
        DummyModel.model_validate_yaml(yaml_data)


@pytest.mark.unit
def test_model_dump_yaml_without_exclusions():
    """Dump YAML without excluding any fields."""
    model = DummyModel(name="Alice", age=25, api_key="secret_key")
    yaml_output = model.model_dump_yaml()
    output_data = yaml.safe_load(yaml_output)
    assert output_data["name"] == "Alice"
    assert output_data["age"] == 25
    assert output_data["api_key"] == "secret_key"


@pytest.mark.unit
def test_model_dump_yaml_with_field_exclusion():
    """Exclude specified fields when dumping."""
    model = DummyModel(name="Alice", age=25, api_key="secret_key")
    yaml_output = model.model_dump_yaml(fields_to_exclude=["age"])
    output_data = yaml.safe_load(yaml_output)
    assert "age" not in output_data
    assert output_data["name"] == "Alice"
    assert output_data["api_key"] == "secret_key"


@pytest.mark.unit
def test_model_dump_yaml_with_api_key_placeholder():
    """Replace API keys with a placeholder when dumping."""
    model = DummyModel(name="Alice", age=25, api_key="secret_key")
    placeholder = "REDACTED"
    yaml_output = model.model_dump_yaml(api_key_placeholder=placeholder)
    output_data = yaml.safe_load(yaml_output)
    assert output_data["api_key"] == placeholder
    assert output_data["name"] == "Alice"
    assert output_data["age"] == 25


@pytest.mark.unit
def test_model_dump_yaml_with_nested_data():
    """Handle nested structures and API key masking."""

    # Test nested dictionary structure and api_key substitution within it
    class NestedModel(YamlMixin):
        name: str
        details: dict

    nested_yaml = """
    name: Charlie
    details:
      api_key: nested_secret
      info: some_info
    """
    model = NestedModel.model_validate_yaml(nested_yaml)
    yaml_output = model.model_dump_yaml(api_key_placeholder="REDACTED")
    output_data = yaml.safe_load(yaml_output)
    assert output_data["name"] == "Charlie"
    assert output_data["details"]["api_key"] == "REDACTED"
    assert output_data["details"]["info"] == "some_info"


@pytest.mark.unit
def test_model_dump_yaml_safe_dump():
    """Ensure output YAML uses safe dumping without Python tags."""
    model = DummyModel(name="Alice", age=25, api_key="secret_key")
    yaml_output = model.model_dump_yaml()
    assert "!!python" not in yaml_output
