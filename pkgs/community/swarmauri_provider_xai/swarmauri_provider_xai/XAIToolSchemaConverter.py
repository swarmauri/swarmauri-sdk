from typing import Any


class XAIToolSchemaConverter:
    def convert(self, tool: Any) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": getattr(tool, "description", None),
                "parameters": {"type": "object", "properties": {}},
            },
        }
