"""IExecutionDriver contract."""

from abc import ABC, abstractmethod

from .models import DriverStep, ExecutionCapabilities, ExecutionSnapshot


class IExecutionDriver(ABC):
    """Define the interchangeable ExecutionDriver contract."""

    @abstractmethod
    def supports(self) -> ExecutionCapabilities: ...

    @abstractmethod
    async def step(self, snapshot: ExecutionSnapshot) -> DriverStep: ...
