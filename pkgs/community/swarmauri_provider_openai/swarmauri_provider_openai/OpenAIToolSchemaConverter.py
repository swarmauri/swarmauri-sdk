from typing import Any


class OpenAIToolSchemaConverter:
    def convert(self, tool: Any) -> dict[str, Any]:
        parameters = getattr(tool, "parameters", [])
        properties = {
            parameter.name: {
                "type": getattr(parameter, "type", "string"),
                "description": getattr(parameter, "description", None),
            }
            for parameter in parameters
        }
        return {
            "type": "function",
            "name": tool.name,
            "description": getattr(tool, "description", None),
            "parameters": {"type": "object", "properties": properties},
        }
