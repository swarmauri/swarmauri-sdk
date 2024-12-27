from typing import Dict, Any, Literal, List
from swarmauri_core.typing import SubclassUnion
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.schema_converters.SchemaConverterBase import SchemaConverterBase

class GeminiSchemaConverter(SchemaConverterBase):
    type: Literal["GeminiSchemaConverter"] = "GeminiSchemaConverter"

    # Define type constants to replace genai.protos.Type
    class Types:
        STRING = "string"
        INTEGER = "integer"
        BOOLEAN = "boolean"
        ARRAY = "array"
        OBJECT = "object"

    def convert(self, tool: SubclassUnion[ToolBase]) -> Dict[str, Any]:
        """
        Convert a tool's parameters into a function declaration schema.
        
        Args:
            tool: The tool to convert
            
        Returns:
            Dict containing the function declaration schema
        """
        properties: Dict[str, Dict[str, str]] = {}
        required: List[str] = []

        for param in tool.parameters:
            properties[param.name] = {
                "type": self.convert_type(param.type),
                "description": param.description,
            }
            if param.required:
                required.append(param.name)

        schema = {
            "type": self.Types.OBJECT,
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
        """
        Convert a parameter type to its corresponding schema type.
        
        Args:
            param_type: The parameter type to convert
            
        Returns:
            The corresponding schema type string
        """
        type_mapping = {
            "string": self.Types.STRING,
            "str": self.Types.STRING,
            "integer": self.Types.INTEGER,
            "int": self.Types.INTEGER,
            "boolean": self.Types.BOOLEAN,
            "bool": self.Types.BOOLEAN,
            "array": self.Types.ARRAY,
            "object": self.Types.OBJECT,
        }
        return type_mapping.get(param_type, self.Types.STRING)