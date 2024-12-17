from abc import ABC, abstractmethod
from typing import Any, Callable, Dict


class ITaskMgtStrategy(ABC):
    """Abstract base class for TaskStrategy."""

    @abstractmethod
    def assign_task(
        self, task: Dict[str, Any], agent_factory: Callable, service_registry: Callable
    ) -> str:
        """
        Abstract method to assign a task to a service.
        """
        pass

    @abstractmethod
    def add_task(self, task: Dict[str, Any]) -> None:
        """
        Abstract method to add a task to the task queue.
        """
        pass

    @abstractmethod
    def remove_task(self, task_id: str) -> None:
        """
        Abstract method to remove a task from the task queue.
        """
        pass

    @abstractmethod
    def get_task(self, task_id: str) -> Dict[str, Any]:
        """
        Abstract method to get a task from the task queue.
        """
        pass

    @abstractmethod
    def process_tasks(self, task: Dict[str, Any]) -> None:
        """
        Abstract method to process a task.
        """
        pass
