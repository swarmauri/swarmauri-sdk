"""Reusable component base for ITaskManager implementations."""

from typing import Literal

from pydantic import ConfigDict, Field
from swarmauri_core.tasks.ITaskManager import ITaskManager
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class TaskManagerBase(ITaskManager, ComponentBase):
    """Keep implementations compatible with component discovery."""

    resource: str = Field(
        default=ResourceTypes.TASK_MANAGER.value, frozen=True
    )
    type: Literal["TaskManagerBase"] = "TaskManagerBase"
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
