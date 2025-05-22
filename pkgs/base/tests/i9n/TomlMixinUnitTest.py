import catoml
import pytest

from swarmauri_base.TomlMixin import TomlMixin


# Integration model combining several features
class IntegrationModel(TomlMixin):
    name: str
    age: int
    api_key: str = None
    details: dict = {}


@pytest.mark.i9n
def test_integration_toml_roundtrip():
    input_toml = """
name = "Diana"
age = 40
api_key = "original_key"

[details]
info = "integrated"
api_key = "inner_key"
"""
    model = IntegrationModel.model_validate_toml(input_toml)

    output_toml = model.model_dump_toml(fields_to_exclude=["age"], api_key_placeholder="REDACTED")
    output_data = catoml.loads(output_toml)

    assert output_data["name"] == "Diana"
    assert "age" not in output_data
    assert output_data["api_key"] == "REDACTED"
    assert output_data["details"]["api_key"] == "REDACTED"
    assert output_data["details"]["info"] == "integrated"


@pytest.mark.i9n
def test_integration_toml_parsing_and_dumping():
    complex_toml = """
name = "Eve"
age = 28
api_key = "top_secret"

[details]
list_of_items = ["item1", "item2"]

[details.nested]
key = "value"
api_key = "inner_secret"
"""
    model = IntegrationModel.model_validate_toml(complex_toml)
    output_toml = model.model_dump_toml(api_key_placeholder="HIDDEN", fields_to_exclude=["age"])
    output_data = catoml.loads(output_toml)

    assert output_data["name"] == "Eve"
    assert "age" not in output_data
    assert output_data["api_key"] == "HIDDEN"
    assert output_data["details"]["nested"]["api_key"] == "HIDDEN"
    assert output_data["details"]["list_of_items"] == ["item1", "item2"]
    assert output_data["details"]["nested"]["key"] == "value"
