from abc import abstractmethod
from typing import Any, Literal

from pydantic import ConfigDict, Field
from swarmauri_core.schema_converters.ISchemaConvert import ISchemaConvert
from swarmauri_core.tools.ITool import ITool

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class SchemaConverterBase(ISchemaConvert, ComponentBase):
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    resource: str | None = Field(
        default=ResourceTypes.SCHEMA_CONVERTER.value, frozen=True
    )
    type: Literal["SchemaConverterBase"] = "SchemaConverterBase"

    @abstractmethod
    def convert(self, tool: ITool) -> dict[str, Any]:
        raise NotImplementedError(
            "Subclasses must implement the convert method."
        )
