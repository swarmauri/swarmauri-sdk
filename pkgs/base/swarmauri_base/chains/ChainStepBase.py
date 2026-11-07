from typing import Any, Literal

from pydantic import Field
from swarmauri_core.chains.IChainStep import IChainStep

from swarmauri_base.ComponentBase import (
    ComponentBase,
    ResourceTypes,
    SubclassUnion,
)
from swarmauri_base.tools.ToolBase import ToolBase


@ComponentBase.register_model()
class ChainStepBase(IChainStep, ComponentBase):
    """
    Represents a single step within an execution chain.
    """

    key: str
    method: SubclassUnion[ToolBase]
    args: tuple = Field(default_factory=tuple)
    kwargs: dict[str, Any] = Field(default_factory=dict)
    ref: str | None = Field(default=None)
    resource: str | None = Field(default=ResourceTypes.CHAINSTEP.value)
    type: Literal["ChainStepBase"] = "ChainStepBase"
