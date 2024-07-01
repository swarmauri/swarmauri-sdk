from abc import abstractmethod
from typing import Optional, Dict, Any, Literal
from pydantic import ConfigDict, Field
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.schema_converters.ISchemaConvert import ISchemaConvert
from swarmauri.core.tools.ITool import ITool

class SchemaConverterBase(ISchemaConvert, ComponentBase):
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    resource: Optional[str] =  Field(default=ResourceTypes.SCHEMA_CONVERTER.value, frozen=True)
    type: Literal['SchemaConverterBase'] = 'SchemaConverterBase'

    @abstractmethod
    def convert(self, tool: ITool) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement the convert method.")
