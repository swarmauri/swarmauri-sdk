"""Reusable component base for IExecutionDriver implementations."""

from typing import Literal

from pydantic import ConfigDict, Field
from swarmauri_core.executions.IExecutionDriver import IExecutionDriver
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class ExecutionDriverBase(IExecutionDriver, ComponentBase):
    """Keep implementations compatible with component discovery."""

    resource: str = Field(
        default=ResourceTypes.EXECUTION_DRIVER.value, frozen=True
    )
    type: Literal["ExecutionDriverBase"] = "ExecutionDriverBase"
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
