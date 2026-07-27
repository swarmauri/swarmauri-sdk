from typing import Any


class QwenToolSchemaConverter:
    def convert(self, tool: Any) -> dict[str, Any]:
        return {
            "type": "function",
            "name": tool.name,
            "parameters": {"type": "object", "properties": {}},
        }
