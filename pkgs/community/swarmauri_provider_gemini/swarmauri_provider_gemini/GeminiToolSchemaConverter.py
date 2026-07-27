from typing import Any, Dict


class GeminiToolSchemaConverter:
    def convert(self, tool: Any) -> Dict[str, Any]:
        parameters = getattr(tool, "parameters", [])
        properties = {
            parameter.name: {
                "type": getattr(parameter, "type", "string"),
                "description": getattr(parameter, "description", None),
            }
            for parameter in parameters
        }
        required = [
            parameter.name
            for parameter in parameters
            if getattr(parameter, "required", False)
        ]
        return {
            "name": tool.name,
            "description": getattr(tool, "description", None),
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }
