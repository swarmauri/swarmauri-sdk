from abc import ABC, abstractmethod
from typing import Any, Callable


class ITaskMgmtStrategy(ABC):
    """Abstract base class for TaskStrategy."""

    @abstractmethod
    def assign_task(
        self,
        task: dict[str, Any],
        agent_factory: Callable,
        service_registry: Callable,
    ) -> str:
        """
        Abstract method to assign a task to a service.
        """

    @abstractmethod
    def add_task(self, task: dict[str, Any]) -> None:
        """
        Abstract method to add a task to the task queue.
        """

    @abstractmethod
    def remove_task(self, task_id: str) -> None:
        """
        Abstract method to remove a task from the task queue.
        """

    @abstractmethod
    def get_task(self, task_id: str) -> dict[str, Any]:
        """
        Abstract method to get a task from the task queue.
        """

    @abstractmethod
    def process_tasks(self, task: dict[str, Any]) -> None:
        """
        Abstract method to process a task.
        """
