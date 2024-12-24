from abc import ABC, abstractmethod
from typing import Optional, List, Any, Literal
from pydantic import Field
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.tools.ParameterBase import ParameterBase
from swarmauri_core.tools.ITool import ITool


class ToolBase(ITool, ComponentBase, ABC):
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
