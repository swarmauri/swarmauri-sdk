from typing import Any, Dict


class XAIToolSchemaConverter:
    def convert(self, tool: Any) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": getattr(tool, "description", None),
                "parameters": {"type": "object", "properties": {}},
            },
        }
