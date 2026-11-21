"""ITaskStore contract."""

from abc import ABC, abstractmethod

from .models import TaskRecord


class ITaskStore(ABC):
    """Define the interchangeable TaskStore contract."""

    @abstractmethod
    def create(self, task: TaskRecord) -> None: ...

    @abstractmethod
    def load(self, task_id: str) -> TaskRecord: ...

    @abstractmethod
    def save(self, task: TaskRecord) -> TaskRecord: ...
