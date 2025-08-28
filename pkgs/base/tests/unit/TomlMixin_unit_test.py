"""Unit tests for ``TomlMixin`` utilities."""

import tomllib
import pytest

from swarmauri_base.TomlMixin import TomlMixin


# --- Dummy model for testing ---
class DummyModel(TomlMixin):
    """Simple model used for TOML tests."""

    name: str
    age: int
    api_key: str | None = None


# --- Unit Tests ---


@pytest.mark.unit
def test_model_validate_toml_success():
    """Validate successful TOML parsing."""
    toml_data = """
    name = "Alice"
    age = 25
    api_key = "secret_key"
    """
    model = DummyModel.model_validate_toml(toml_data)
    assert model.name == "Alice"
    assert model.age == 25
    assert model.api_key == "secret_key"


@pytest.mark.unit
def test_model_validate_toml_invalid_toml():
    """Raise ``ValueError`` when TOML is malformed."""
    invalid_toml = """
    name = "Alice"
    age 25
    api_key = "secret_key"
    """
    with pytest.raises(ValueError, match="Invalid TOML data"):
        DummyModel.model_validate_toml(invalid_toml)


@pytest.mark.unit
def test_model_validate_toml_validation_error():
    """Handle invalid field types during parsing."""
    toml_data = """
    name = "Bob"
    age = "not_a_number"
    api_key = "secret_key"
    """
    with pytest.raises(ValueError, match="Validation failed"):
        DummyModel.model_validate_toml(toml_data)


@pytest.mark.unit
def test_model_dump_toml_without_exclusions():
    """Dump TOML without excluding any fields."""
    model = DummyModel(name="Alice", age=25, api_key="secret_key")
    toml_output = model.model_dump_toml()
    output_data = tomllib.loads(toml_output)
    assert output_data["name"] == "Alice"
    assert output_data["age"] == 25
    assert output_data["api_key"] == "secret_key"


@pytest.mark.unit
def test_model_dump_toml_with_field_exclusion():
    """Exclude specified fields when dumping."""
    model = DummyModel(name="Alice", age=25, api_key="secret_key")
    toml_output = model.model_dump_toml(fields_to_exclude=["age"])
    output_data = tomllib.loads(toml_output)
    assert "age" not in output_data
    assert output_data["name"] == "Alice"
    assert output_data["api_key"] == "secret_key"


@pytest.mark.unit
def test_model_dump_toml_with_api_key_placeholder():
    """Replace API keys with a placeholder when dumping."""
    model = DummyModel(name="Alice", age=25, api_key="secret_key")
    placeholder = "REDACTED"
    toml_output = model.model_dump_toml(api_key_placeholder=placeholder)
    output_data = tomllib.loads(toml_output)
    assert output_data["api_key"] == placeholder
    assert output_data["name"] == "Alice"
    assert output_data["age"] == 25


@pytest.mark.unit
def test_model_dump_toml_with_nested_data():
    """Handle nested structures and API key masking."""

    class NestedModel(TomlMixin):
        name: str
        details: dict

    nested_toml = """
    name = "Charlie"

    [details]
    api_key = "nested_secret"
    info = "some_info"
    """
    model = NestedModel.model_validate_toml(nested_toml)
    toml_output = model.model_dump_toml(api_key_placeholder="REDACTED")
    output_data = tomllib.loads(toml_output)
    assert output_data["name"] == "Charlie"
    assert output_data["details"]["api_key"] == "REDACTED"
    assert output_data["details"]["info"] == "some_info"
