from typing import Dict, Any, Literal
import google.generativeai as genai
from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.schema_converters.base.SchemaConverterBase import SchemaConverterBase

class GeminiSchemaConverter(SchemaConverterBase):
    type: Literal['GeminiSchemaConverter'] = 'GeminiSchemaConverter'

    def convert(self, tool: SubclassUnion[ToolBase]) -> genai.FunctionDeclaration:
        properties = {}
        required = []

        for param in tool.parameters:
            properties[param.name] = genai.Schema(
                type=self.convert_type(param.type),
                description=param.description
            )
            if param.required:
                required.append(param.name)

        schema = genai.Schema(
            type=genai.Type.OBJECT,
            properties=properties,
            required=required
        )

        return genai.FunctionDeclaration(
            name=tool.name,
            description=tool.description,
            parameters=schema
        )

    def convert_type(self, param_type: str) -> genai.Type:
        type_mapping = {
            "string": genai.Type.STRING,
            "str": genai.Type.STRING,
            "integer": genai.Type.INTEGER,
            "int": genai.Type.INTEGER,
            "boolean": genai.Type.BOOLEAN,
            "bool": genai.Type.BOOLEAN,
            "array": genai.Type.ARRAY,
            "object": genai.Type.OBJECT
        }
        return type_mapping.get(param_type, genai.Type.STRING)