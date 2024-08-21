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

        function_declaration = genai.protos.FunctionDeclaration(
            name=tool.name,
            description=tool.description,
            parameters=schema
        )

        return self.to_serializable(function_declaration)

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

    def to_serializable(self, function_declaration: genai.protos.FunctionDeclaration) -> Dict[str, Any]:
        """Converts FunctionDeclaration to a serializable dictionary."""
        return {
            "name": function_declaration.name,
            "description": function_declaration.description,
            "parameters": {
                "type": function_declaration.parameters.type,
                "properties": {
                    k: {
                        "type": v.type,
                        "description": v.description
                    } for k, v in function_declaration.parameters.properties.items()
                },
                "required": function_declaration.parameters.required
            }
        }
