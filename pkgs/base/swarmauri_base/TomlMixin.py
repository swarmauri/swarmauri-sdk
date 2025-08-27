"""Mixin for TOML serialization and validation utilities."""

import json
import tomllib
import toml
from pydantic import BaseModel, ValidationError


class TomlMixin(BaseModel):
    """Provide TOML-based validation and serialization helpers."""

    @classmethod
    def model_validate_toml(cls, toml_data: str):
        """Validate a model from a TOML string."""
        try:
            # Parse TOML into a Python dictionary
            toml_content = tomllib.loads(toml_data)

            # Convert the dictionary to JSON and validate using Pydantic
            return cls.model_validate_json(json.dumps(toml_content))
        except tomllib.TOMLDecodeError as e:
            raise ValueError(f"Invalid TOML data: {e}")
        except ValidationError as e:
            raise ValueError(f"Validation failed: {e}")

    def model_dump_toml(self, fields_to_exclude=None, api_key_placeholder=None):
        """Return a TOML representation of the model."""
        if fields_to_exclude is None:
            fields_to_exclude = []

        # Load the JSON string into a Python dictionary
        json_data = json.loads(self.model_dump_json())

        # Function to recursively remove specific keys and handle api_key placeholders
        def process_fields(data, fields_to_exclude):
            """Recursively filter fields and apply placeholders."""
            if isinstance(data, dict):
                return {
                    key: (
                        api_key_placeholder
                        if key == "api_key" and api_key_placeholder is not None
                        else process_fields(value, fields_to_exclude)
                    )
                    for key, value in data.items()
                    if key not in fields_to_exclude
                }
            elif isinstance(data, list):
                return [process_fields(item, fields_to_exclude) for item in data]
            else:
                return data

        # Filter the JSON data
        filtered_data = process_fields(json_data, fields_to_exclude)

        # Convert the filtered data into TOML
        return toml.dumps(filtered_data)
