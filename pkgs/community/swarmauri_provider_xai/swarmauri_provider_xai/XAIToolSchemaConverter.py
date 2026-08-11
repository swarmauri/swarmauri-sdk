from typing import Any


class XAIToolSchemaConverter:
    def convert(self, tool: Any) -> dict[str, Any]:
        properties: dict[str, Any] = {}
        required: list[str] = []
        for parameter in getattr(tool, "parameters", []):
            schema: dict[str, Any] = {
                "type": parameter.input_type,
                "description": parameter.description,
            }
            if parameter.enum:
                schema["enum"] = parameter.enum
            properties[parameter.name] = schema
            if parameter.required:
                required.append(parameter.name)
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": getattr(tool, "description", None),
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                    "additionalProperties": False,
                },
            },
        }
