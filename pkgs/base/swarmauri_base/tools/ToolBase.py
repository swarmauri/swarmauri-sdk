# File: swarmauri_core/tools/ToolBase.py

from abc import abstractmethod
from typing import Any, List, Optional, Literal
from pydantic import Field

from swarmauri_core.tools.ITool import ITool
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.tools.ParameterBase import ParameterBase


@ComponentBase.register_model()
class ToolBase(ITool, ComponentBase):
    """
    File: ToolBase.py
    Class: ToolBase

    Base class for all tools. Now supports both single‐call (__call__)
    and batch processing via `batch()`.
    """

    name: str
    description: Optional[str] = None
    parameters: List[ParameterBase] = Field(default_factory=list)
    resource: Optional[str] = Field(default=ResourceTypes.TOOL.value)
    type: Literal["ToolBase"] = "ToolBase"

    def call(self, *args, **kwargs) -> Any:
        """
        File: ToolBase.py
        Class: ToolBase
        Method: call

        Alias for __call__ to conform to ITool interface.
        """
        return self.__call__(*args, **kwargs)

    @abstractmethod
    def __call__(self, *args, **kwargs) -> Any:
        """
        File: ToolBase.py
        Class: ToolBase
        Method: __call__

        Subclasses must implement their single‐item logic here.
        """
        raise NotImplementedError("Subclasses must implement the __call__ method.")

    def batch(self, inputs: List[Any], *args, **kwargs) -> List[Any]:
        """
        File: ToolBase.py
        Class: ToolBase
        Method: batch

        Default batch implementation: calls __call__ on each item in `inputs`.
        Subclasses can override for optimized bulk behavior.
        """
        results: List[Any] = []
        for inp in inputs:
            results.append(self.__call__(inp, **kwargs))
        return results
