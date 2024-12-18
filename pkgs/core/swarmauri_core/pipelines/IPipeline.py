from abc import ABC, abstractmethod
from typing import Any, Callable, List
from enum import Enum


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
        pass

    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> List[Any]:
        """
        Execute the entire pipeline.

        :return: List of results from pipeline execution
        """
        pass

    @abstractmethod
    def get_status(self) -> PipelineStatus:
        """
        Get the current status of the pipeline.

        :return: Current pipeline status
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """
        Reset the pipeline to its initial state.
        """
        pass
