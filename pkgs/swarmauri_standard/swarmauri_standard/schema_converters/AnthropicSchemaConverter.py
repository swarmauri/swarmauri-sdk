from typing import Any, Dict, Literal

from swarmauri_base.ComponentBase import ComponentBase, SubclassUnion
from swarmauri_base.schema_converters.SchemaConverterBase import SchemaConverterBase
from swarmauri_base.tools.ToolBase import ToolBase


@ComponentBase.register_type(SchemaConverterBase, "AnthropicSchemaConverter")
class AnthropicSchemaConverter(SchemaConverterBase):
    type: Literal["AnthropicSchemaConverter"] = "AnthropicSchemaConverter"

    def convert(self, tool: SubclassUnion[ToolBase]) -> Dict[str, Any]:
        properties = {}
        required = []

        for param in tool.parameters:
            properties[param.name] = {
                "type": param.input_type,
                "description": param.description,
            }
            if param.required:
                required.append(param.name)

        return {
            "name": tool.name,
            "description": tool.description,
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }
