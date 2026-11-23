"""Reusable component base for IExecutionController implementations."""

from typing import Literal

from pydantic import ConfigDict, Field
from swarmauri_core.executions.IExecutionController import IExecutionController
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class ExecutionControllerBase(IExecutionController, ComponentBase):
    """Keep implementations compatible with component discovery."""

    resource: str = Field(
        default=ResourceTypes.EXECUTION_CONTROLLER.value, frozen=True
    )
    type: Literal["ExecutionControllerBase"] = "ExecutionControllerBase"
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
