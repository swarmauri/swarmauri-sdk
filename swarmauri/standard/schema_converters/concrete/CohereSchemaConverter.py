from typing import Dict, Any, Literal
from swarmauri.core.typing import SubclassUnion
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.tools.base.SchemaConverterBase import SchemaConverterBase

class CohereSchemaConverter(SchemaConverterBase):
    type: Literal['CohereSchemaConverter'] = 'CohereSchemaConverter'

    def convert(self, tool: SubclassUnion[ToolBase]) -> Dict[str, Any]:
        properties = {}
        required = []

        for param_name, param_details in tool.parameter_definitions.items():
            properties[param_name] = {
                "type": param_details['type'],
                "description": param_details['description'],
            }
            if 'enum' in param_details:
                properties[param_name]['enum'] = param_details['enum']

            if param_details['required']:
                required.append(param_name)

        return {
            "name": tool.name,
            "description": tool.description,
            "parameter_definitions": {
                "type": "object",
                "properties": properties,
                "required": required,
            }
        }