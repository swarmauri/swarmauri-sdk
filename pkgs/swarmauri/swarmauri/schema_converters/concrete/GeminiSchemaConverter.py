from typing import Dict, Any, Literal
import google.generativeai as genai
from swarmauri_core.typing import SubclassUnion
from swarmauri.tools.base.ToolBase import ToolBase
from swarmauri.schema_converters.base.SchemaConverterBase import (
    SchemaConverterBase,
)


class GeminiSchemaConverter(SchemaConverterBase):
    type: Literal["GeminiSchemaConverter"] = "GeminiSchemaConverter"

    def convert(self, tool: SubclassUnion[ToolBase]) -> Dict[str, Any]:
        properties = {}
        required = []

        for param in tool.parameters:
            properties[param.name] = {
                "type": self.convert_type(param.type),
                "description": param.description,
            }
            if param.required:
                required.append(param.name)

        schema = {
            "type": genai.protos.Type.OBJECT,
            "properties": properties,
            "required": required,
        }

        function_declaration = {
            "name": tool.name,
            "description": tool.description,
            "parameters": schema,
        }

        return function_declaration

    def convert_type(self, param_type: str) -> str:
        type_mapping = {
            "string": genai.protos.Type.STRING,
            "str": genai.protos.Type.STRING,
            "integer": genai.protos.Type.INTEGER,
            "int": genai.protos.Type.INTEGER,
            "boolean": genai.protos.Type.BOOLEAN,
            "bool": genai.protos.Type.BOOLEAN,
            "array": genai.protos.Type.ARRAY,
            "object": genai.protos.Type.OBJECT,
        }
        return type_mapping.get(param_type, "string")
