from typing import Any


class OpenRouterToolSchemaConverter:
    def convert(self, tool: Any) -> dict[str, Any]:
        properties: dict[str, Any] = {}
        required: list[str] = []
        for parameter in getattr(tool, "parameters", []):
            schema: dict[str, Any] = {
                "type": getattr(parameter, "input_type", "string"),
                "description": getattr(parameter, "description", None),
            }
            enum = getattr(parameter, "enum", None)
            if enum:
                schema["enum"] = enum
            properties[parameter.name] = schema
            if getattr(parameter, "required", False):
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
