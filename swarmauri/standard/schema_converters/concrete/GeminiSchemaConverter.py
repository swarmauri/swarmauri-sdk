from typing import Dict, Any, Literal
import google.generativeai as genai
from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.schema_converters.base.SchemaConverterBase import SchemaConverterBase

class GeminiSchemaConverter(SchemaConverterBase):
    type: Literal['GeminiSchemaConverter'] = 'GeminiSchemaConverter'

    def convert(self, tool: SubclassUnion[ToolBase]) -> Dict[str, Any]:
        properties = {}
        required = []

        for param in tool.parameters:
            properties[param.name] = {
                "type": self.convert_type(param.type),
                "description": param.description
            }
            if param.required:
                required.append(param.name)

        schema = {
            "type": "object",
            "properties": properties,
            "required": required
        }

        function_declaration = {
            "name": tool.name,
            "description": tool.description,
            "parameters": schema
        }

        return function_declaration

    def convert_type(self, param_type: str) -> str:
        type_mapping = {
            "string": "string",
            "str": "string",
            "integer": "integer",
            "int": "integer",
            "boolean": "boolean",
            "bool": "boolean",
            "array": "array",
            "object": "object"
        }
        return type_mapping.get(param_type, "string")
