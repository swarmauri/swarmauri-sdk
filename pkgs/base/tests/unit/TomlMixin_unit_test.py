import pytest
import catoml

from swarmauri_base.TomlMixin import TomlMixin


# --- Dummy model for testing ---
class DummyModel(TomlMixin):
    name: str
    age: int
    api_key: str = None


# --- Unit Tests ---


@pytest.mark.unit
def test_model_validate_toml_success():
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
    invalid_toml = """
name = "Alice"
age = 25
api_key =
"""
    with pytest.raises(ValueError, match="Invalid TOML data"):
        DummyModel.model_validate_toml(invalid_toml)


@pytest.mark.unit
def test_model_validate_toml_validation_error():
    toml_data = """
name = "Bob"
age = "not_a_number"
api_key = "secret_key"
"""
    with pytest.raises(ValueError, match="Validation failed"):
        DummyModel.model_validate_toml(toml_data)


@pytest.mark.unit
def test_model_dump_toml_without_exclusions():
    model = DummyModel(name="Alice", age=25, api_key="secret_key")
    toml_output = model.model_dump_toml()
    output_data = catoml.loads(toml_output)
    assert output_data["name"] == "Alice"
    assert output_data["age"] == 25
    assert output_data["api_key"] == "secret_key"


@pytest.mark.unit
def test_model_dump_toml_with_field_exclusion():
    model = DummyModel(name="Alice", age=25, api_key="secret_key")
    toml_output = model.model_dump_toml(fields_to_exclude=["age"])
    output_data = catoml.loads(toml_output)
    assert "age" not in output_data
    assert output_data["name"] == "Alice"
    assert output_data["api_key"] == "secret_key"


@pytest.mark.unit
def test_model_dump_toml_with_api_key_placeholder():
    model = DummyModel(name="Alice", age=25, api_key="secret_key")
    placeholder = "REDACTED"
    toml_output = model.model_dump_toml(api_key_placeholder=placeholder)
    output_data = catoml.loads(toml_output)
    assert output_data["api_key"] == placeholder
    assert output_data["name"] == "Alice"
    assert output_data["age"] == 25


@pytest.mark.unit
def test_model_dump_toml_with_nested_data():
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
    output_data = catoml.loads(toml_output)
    assert output_data["name"] == "Charlie"
    assert output_data["details"]["api_key"] == "REDACTED"
    assert output_data["details"]["info"] == "some_info"
