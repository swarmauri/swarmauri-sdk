"""Reusable component base for ITaskStore implementations."""

from typing import Literal

from pydantic import ConfigDict, Field
from swarmauri_core.tasks.ITaskStore import ITaskStore
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class TaskStoreBase(ITaskStore, ComponentBase):
    """Keep implementations compatible with component discovery."""

    resource: str = Field(default=ResourceTypes.TASK_STORE.value, frozen=True)
    type: Literal["TaskStoreBase"] = "TaskStoreBase"
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
