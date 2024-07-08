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
                "description": param.description,
                "required": param.required
            }
            if param.type == 'string':
                _type = 'string'
            elif param.type == 'float':
                _type = 'number'
            elif param.type == 'integer':
                _type = 'number'
            elif param.type == 'boolean':
                _type = 'boolean'
            else:
                raise NotImplementedError(f'🚧 Support for missing type pending https://docs.cohere.com/docs/parameter-types-in-tool-use\n: Missing Type: {param.type}')
            properties[param.name].update({'type': _type})

        return {
            "name": tool.name,
            "description": tool.description,
            "parameter_definitions": properties
        }