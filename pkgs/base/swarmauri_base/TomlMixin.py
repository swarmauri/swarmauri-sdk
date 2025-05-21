import json
from pydantic import BaseModel, ValidationError
import catoml


class TomlMixin(BaseModel):
    @classmethod
    def model_validate_toml(cls, toml_data: str):
        try:
            toml_content = catoml.loads(toml_data)
            return cls.model_validate_json(json.dumps(toml_content))
        except ValueError as e:
            raise ValueError(f"Invalid TOML data: {e}")
        except ValidationError as e:
            raise ValueError(f"Validation failed: {e}")

    def model_dump_toml(self, fields_to_exclude=None, api_key_placeholder=None):
        if fields_to_exclude is None:
            fields_to_exclude = []

        json_data = json.loads(self.model_dump_json())

        def process_fields(data, fields_to_exclude):
            if isinstance(data, dict):
                return {
                    key: (
                        api_key_placeholder if key == "api_key" and api_key_placeholder is not None else process_fields(value, fields_to_exclude)
                    )
                    for key, value in data.items()
                    if key not in fields_to_exclude
                }
            elif isinstance(data, list):
                return [process_fields(item, fields_to_exclude) for item in data]
            else:
                return data

        filtered_data = process_fields(json_data, fields_to_exclude)
        return catoml.dumps(filtered_data)
