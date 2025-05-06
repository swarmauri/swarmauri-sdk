from typing import Dict, Any, Literal
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.schema_converters.SchemaConverterBase import SchemaConverterBase
from swarmauri_base.ComponentBase import ComponentBase, SubclassUnion


@ComponentBase.register_type(SchemaConverterBase, "MistralSchemaConverter")
class MistralSchemaConverter(SchemaConverterBase):
    type: Literal["MistralSchemaConverter"] = "MistralSchemaConverter"

    def convert(self, tool: SubclassUnion[ToolBase]) -> Dict[str, Any]:
        properties = {}
        required = []

        for param in tool.parameters:
            properties[param.name] = {
                "type": param.input_type,
                "description": param.description,
            }
            if param.enum:
                properties[param.name]["enum"] = param.enum

            if param.required:
                required.append(param.name)

        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }
