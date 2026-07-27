from typing import Any, Dict


class AmazonNovaToolSchemaConverter:
    def convert(self, tool: Any) -> Dict[str, Any]:
        return {
            "toolSpec": {
                "name": tool.name,
                "description": getattr(tool, "description", ""),
                "inputSchema": {"json": {"type": "object", "properties": {}}},
            }
        }
