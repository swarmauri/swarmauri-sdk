from abc import abstractmethod

from pydantic import ConfigDict, Field
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.task_mgt_strategies.ITaskMgtStrategy import ITaskMgtStrategy
from typing import Any, Callable, Dict, Literal, Optional


class TaskMgtStrategyBase(ITaskMgtStrategy, ComponentBase):
    """Base class for TaskStrategy."""

    type: Literal["TaskMgtStrategyBase"] = "TaskMgtStrategyBase"
    resource: Optional[str] = Field(
        default=ResourceTypes.TASK_MGT_STRATEGY.value, frozen=True
    )
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    @abstractmethod
    def assign_task(
        self, task: Dict[str, Any], agent_factory: Callable, service_registry: Callable
    ) -> str:
        """
        Abstract method to assign a task to a service.
        """
        raise NotImplementedError(
            "assign_task method must be implemented in derived classes."
        )

    @abstractmethod
    def add_task(self, task: Dict[str, Any]) -> None:
        """
        Abstract method to add a task to the task queue.
        """
        raise NotImplementedError(
            "add_task method must be implemented in derived classes."
        )

    @abstractmethod
    def remove_task(self, task_id: str) -> None:
        """
        Abstract method to remove a task from the task queue.
        """
        raise NotImplementedError(
            "remove_task method must be implemented in derived classes."
        )

    @abstractmethod
    def get_task(self, task_id: str) -> Dict[str, Any]:
        """
        Abstract method to get a task from the task queue.
        """
        raise NotImplementedError(
            "get_task method must be implemented in derived classes."
        )

    @abstractmethod
    def process_tasks(self, task: Dict[str, Any]) -> None:
        """
        Abstract method to process tasks.
        """
        raise NotImplementedError(
            "process_task method must be implemented in derived classes."
        )
