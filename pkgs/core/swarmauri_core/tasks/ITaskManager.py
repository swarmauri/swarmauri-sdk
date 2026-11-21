"""ITaskManager contract."""

from abc import ABC, abstractmethod

from .models import TaskRecord
from swarmauri_core.permissions import Permission


class ITaskManager(ABC):
    """Define the interchangeable TaskManager contract."""

    @abstractmethod
    def start(
        self,
        subject: str,
        tenant: str,
        permissions: tuple[Permission, ...],
        expires_at: int,
    ) -> TaskRecord: ...

    @abstractmethod
    def pause(self, task_id: str) -> TaskRecord: ...

    @abstractmethod
    def resume(self, task_id: str) -> TaskRecord: ...

    @abstractmethod
    def stop(self, task_id: str) -> TaskRecord: ...
