"""Reusable component base for IInvoker implementations."""

from typing import Literal

from pydantic import ConfigDict, Field
from swarmauri_core.invocations.IInvoker import IInvoker
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class InvokerBase(IInvoker, ComponentBase):
    """Keep implementations compatible with component discovery."""

    resource: str = Field(default=ResourceTypes.INVOKER.value, frozen=True)
    type: Literal["InvokerBase"] = "InvokerBase"
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
