from typing import  Dict, Any, Literal
from swarmauri_core.typing import SubclassUnion
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.schema_converters.SchemaConverterBase import SchemaConverterBase

class AnthropicSchemaConverter(SchemaConverterBase):
    type: Literal['AnthropicSchemaConverter'] = 'AnthropicSchemaConverter'

    def convert(self, tool: SubclassUnion[ToolBase]) -> Dict[str, Any]:
        properties = {}
        required = []

        for param in tool.parameters:
            properties[param.name] = {
                "type": param.type,
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
            }
        }
