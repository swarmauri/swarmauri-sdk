from typing import Dict, Any, Literal
import google.generativeai as genai
from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.schema_converters.base.SchemaConverterBase import SchemaConverterBase

class GeminiSchemaConverter(SchemaConverterBase):
    type: Literal['GeminiSchemaConverter'] = 'GeminiSchemaConverter'

    def convert(self, tool: SubclassUnion[ToolBase]) -> genai.protos.FunctionDeclaration:
        properties = {}
        required = []

        for param in tool.parameters:
            properties[param.name] = genai.protos.Schema(
                type=self.convert_type(param.type),
                description=param.description
            )
            if param.required:
                required.append(param.name)

        schema = genai.protos.Schema(
            type=genai.protos.Type.OBJECT,
            properties=properties,
            required=required
        )

        return genai.protos.FunctionDeclaration(
            name=tool.name,
            description=tool.description,
            parameters=schema
        )

    def convert_type(self, param_type: str) -> genai.protos.Type:
        type_mapping = {
            "string": genai.protos.Type.STRING,
            "str": genai.protos.Type.STRING,
            "integer": genai.protos.Type.INTEGER,
            "int": genai.protos.Type.INTEGER,
            "boolean": genai.protos.Type.BOOLEAN,
            "bool": genai.protos.Type.BOOLEAN,
            "array": genai.protos.Type.ARRAY,
            "object": genai.protos.Type.OBJECT
        }
        return type_mapping.get(param_type, genai.protos.Type.STRING)