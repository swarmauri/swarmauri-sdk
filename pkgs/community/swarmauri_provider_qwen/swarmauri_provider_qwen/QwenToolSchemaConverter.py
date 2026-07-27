from typing import Any, Dict


class QwenToolSchemaConverter:
    def convert(self, tool: Any) -> Dict[str, Any]:
        return {
            "type": "function",
            "name": tool.name,
            "parameters": {"type": "object", "properties": {}},
        }
