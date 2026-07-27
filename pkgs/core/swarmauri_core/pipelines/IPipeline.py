from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Callable


class PipelineStatus(Enum):
    """
    Enum representing the status of a pipeline execution.
    """

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"


class IPipeline(ABC):
    """
    Interface defining core methods for pipeline execution and management.
    """

    @abstractmethod
    def add_task(self, task: Callable, *args: Any, **kwargs: Any) -> None:
        """
        Add a task to the pipeline.

        :param task: Callable task to be executed
        :param args: Positional arguments for the task
        :param kwargs: Keyword arguments for the task
        """

    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> list[Any]:
        """
        Execute the entire pipeline.

        :return: List of results from pipeline execution
        """

    @abstractmethod
    def get_status(self) -> PipelineStatus:
        """
        Get the current status of the pipeline.

        :return: Current pipeline status
        """

    @abstractmethod
    def reset(self) -> None:
        """
        Reset the pipeline to its initial state.
        """
