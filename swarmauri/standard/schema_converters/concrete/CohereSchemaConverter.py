from typing import Dict, Any, Literal
from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.schema_converters.base.SchemaConverterBase import SchemaConverterBase

class CohereSchemaConverter(SchemaConverterBase):
    type: Literal['CohereSchemaConverter'] = 'CohereSchemaConverter'

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
            "parameter_definitions": {
                "type": "object",
                "properties": properties,
                "required": required,
            }
        }