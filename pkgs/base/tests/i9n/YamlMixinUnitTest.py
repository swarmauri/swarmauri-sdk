"""Integration tests for the ``YamlMixin`` helpers."""

import yaml
import pytest

from swarmauri_base.YamlMixin import YamlMixin


class IntegrationModel(YamlMixin):
    """Model used to validate YAML round-trip behavior."""

    name: str
    age: int
    api_key: str = None
    details: dict = {}


@pytest.mark.i9n
def test_integration_yaml_roundtrip():
    """Validate YAML dumping and reloading."""
    input_yaml = """
    name: Diana
    age: 40
    api_key: original_key
    details:
      info: integrated
      api_key: inner_key
    """
    # Step 1: Validate YAML and create model instance.
    model = IntegrationModel.model_validate_yaml(input_yaml)

    # Step 2: Dump model to YAML with exclusions and placeholder replacement.
    output_yaml = model.model_dump_yaml(
        fields_to_exclude=["age"], api_key_placeholder="REDACTED"
    )
    output_data = yaml.safe_load(output_yaml)

    # Step 3: Assert that the output has been transformed correctly.
    assert output_data["name"] == "Diana"
    assert "age" not in output_data
    assert output_data["api_key"] == "REDACTED"
    assert output_data["details"]["api_key"] == "REDACTED"
    assert output_data["details"]["info"] == "integrated"


@pytest.mark.i9n
def test_integration_yaml_parsing_and_dumping():
    """Ensure nested data is parsed and dumped correctly."""

    # More complex YAML with nested lists and dictionaries.
    complex_yaml = """
    name: Eve
    age: 28
    api_key: top_secret
    details:
      list_of_items:
        - item1
        - item2
      nested:
        key: value
        api_key: inner_secret
    """
    # Parse YAML into model.
    model = IntegrationModel.model_validate_yaml(complex_yaml)
    # Dump to YAML with a placeholder and excluding the "age" field.
    output_yaml = model.model_dump_yaml(
        api_key_placeholder="HIDDEN", fields_to_exclude=["age"]
    )
    output_data = yaml.safe_load(output_yaml)

    # Validate transformations.
    assert output_data["name"] == "Eve"
    assert "age" not in output_data
    assert output_data["api_key"] == "HIDDEN"
    assert output_data["details"]["nested"]["api_key"] == "HIDDEN"
    assert output_data["details"]["list_of_items"] == ["item1", "item2"]
    assert output_data["details"]["nested"]["key"] == "value"
