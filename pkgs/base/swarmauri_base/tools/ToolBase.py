from abc import abstractmethod
from typing import Optional, List, Literal
from pydantic import Field

from swarmauri_core.tools.ITool import ITool
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.tools.ParameterBase import ParameterBase


@ComponentBase.register_model()
class ToolBase(ITool, ComponentBase):
    name: str
    description: Optional[str] = None
    parameters: List[ParameterBase] = Field(default_factory=list)
    resource: Optional[str] = Field(default=ResourceTypes.TOOL.value)
    type: Literal["ToolBase"] = "ToolBase"

    def call(self, *args, **kwargs):
        return self.__call__(*args, **kwargs)

    @abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement the __call__ method.")
