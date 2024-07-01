from typing import Optional
from pydantic import ConfigDict, Field
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.schema_converters.ISchemaConvert import ISchemaConvert

class SchemaConverterBase(ISchemaConvert, ComponentBase):
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    resource: Optional[str] =  Field(default=ResourceTypes.SCHEMA_CONVERTER.value, frozen=True)
    type: Literal['SchemaConverterBase'] = 'SchemaConverterBase'

    @abstractmethod
    def convert(self, tool: ITool) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement the convert method.")
