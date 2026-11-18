"""IExecutionController contract."""

from abc import ABC, abstractmethod

from .models import DriverStep, ExecutionCapabilities, ExecutionSnapshot


class IExecutionController(ABC):
    """Define the interchangeable ExecutionController contract."""

    @abstractmethod
    def start(
        self,
        task_id: str,
        driver: str,
        state: dict | None = None,
        parent_id: str | None = None,
    ) -> ExecutionSnapshot: ...

    @abstractmethod
    def get(self, execution_id: str) -> ExecutionSnapshot: ...

    @abstractmethod
    async def advance(self, execution_id: str) -> ExecutionSnapshot: ...

    @abstractmethod
    def pause(self, execution_id: str) -> ExecutionSnapshot: ...

    @abstractmethod
    def resume(self, execution_id: str) -> ExecutionSnapshot: ...

    @abstractmethod
    def stop(self, execution_id: str) -> ExecutionSnapshot: ...
