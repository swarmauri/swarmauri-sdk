import json
import yaml
from pydantic import BaseModel, ValidationError


class YamlMixin(BaseModel):
    @classmethod
    def model_validate_yaml(cls, yaml_data: str):
        try:
            # Parse YAML into a Python dictionary
            yaml_content = yaml.safe_load(yaml_data)

            # Convert the dictionary to JSON and validate using Pydantic
            return cls.model_validate_json(json.dumps(yaml_content))
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML data: {e}")
        except ValidationError as e:
            raise ValueError(f"Validation failed: {e}")

    def model_dump_yaml(self, fields_to_exclude=None, api_key_placeholder=None):
        if fields_to_exclude is None:
            fields_to_exclude = []

        # Load the JSON string into a Python dictionary
        json_data = json.loads(self.model_dump_json())

        # Function to recursively remove specific keys and handle api_key placeholders
        def process_fields(data, fields_to_exclude):
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

        # Convert the filtered data into YAML
        return yaml.dump(filtered_data, default_flow_style=False)
