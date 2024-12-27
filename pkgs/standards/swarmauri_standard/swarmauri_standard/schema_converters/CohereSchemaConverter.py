from typing import Dict, Any, Literal
from swarmauri_core.typing import SubclassUnion
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.schema_converters.SchemaConverterBase import SchemaConverterBase

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
                _type = 'str'
            elif param.type == 'float':
                _type = 'float'
            elif param.type == 'integer':
                _type = 'int'
            elif param.type == 'boolean':
                _type = 'bool'
            else:
                raise NotImplementedError(f'🚧 Support for missing type pending https://docs.cohere.com/docs/parameter-types-in-tool-use\n: Missing Type: {param.type}')
            properties[param.name].update({'type': _type})

        return {
            "name": tool.name,
            "description": tool.description,
            "parameter_definitions": properties
        }