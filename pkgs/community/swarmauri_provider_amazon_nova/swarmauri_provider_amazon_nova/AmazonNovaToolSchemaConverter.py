from typing import Any


class AmazonNovaToolSchemaConverter:
    def convert(self, tool: Any) -> dict[str, Any]:
        return {
            "toolSpec": {
                "name": tool.name,
                "description": getattr(tool, "description", ""),
                "inputSchema": {"json": {"type": "object", "properties": {}}},
            }
        }
