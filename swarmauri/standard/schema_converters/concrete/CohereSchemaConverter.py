from typing import Dict, Any, Literal
from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.schema_converters.base.SchemaConverterBase import SchemaConverterBase

class CohereSchemaConverter(SchemaConverterBase):
    type: Literal['CohereSchemaConverter'] = 'CohereSchemaConverter'

    def convert(self, tool: SubclassUnion[ToolBase]) -> Dict[str, Any]:
        properties = {}

        for param in tool.parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description,
                "required": param.required
            }

        return {
            "name": tool.name,
            "description": tool.description,
            "parameter_definitions": properties
        }