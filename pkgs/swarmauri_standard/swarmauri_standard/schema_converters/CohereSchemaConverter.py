from typing import Dict, Any, Literal
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.schema_converters.SchemaConverterBase import SchemaConverterBase
from swarmauri_base.ComponentBase import ComponentBase, SubclassUnion


@ComponentBase.register_type(SchemaConverterBase, "CohereSchemaConverter")
class CohereSchemaConverter(SchemaConverterBase):
    type: Literal["CohereSchemaConverter"] = "CohereSchemaConverter"

    def convert(self, tool: SubclassUnion[ToolBase]) -> Dict[str, Any]:
        properties = {}

        for param in tool.parameters:
            properties[param.name] = {
                "description": param.description,
                "required": param.required,
            }
            if param.input_type == "string":
                _type = "str"
            elif param.input_type == "float":
                _type = "float"
            elif param.input_type == "integer":
                _type = "int"
            elif param.input_type == "boolean":
                _type = "bool"
            else:
                raise NotImplementedError(
                    f"🚧 Support for missing type pending https://docs.cohere.com/docs/parameter-types-in-tool-use\n: Missing Type: {param.input_type}"
                )
            properties[param.name].update({"type": _type})

        return {
            "name": tool.name,
            "description": tool.description,
            "parameter_definitions": properties,
        }
