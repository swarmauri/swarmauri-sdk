from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class RuntimeBase(ABC):
    """Contract for all runtime implementations."""

    def __init__(self, kernel: Any) -> None:
        self.kernel = kernel
        self.executors: dict[str, Any] = {}

    @abstractmethod
    def compile(self, *args: Any, **kwargs: Any) -> tuple[Any, Any | None]:
        """Delegate compilation/planning to the underlying kernel."""

    @abstractmethod
    def register_executor(self, executor: Any) -> None:
        """Register an executor implementation."""

    @abstractmethod
    async def invoke(
        self,
        *,
        executor: str,
        env: Any,
        ctx: Any,
        plan: Any,
        packed_plan: Any | None = None,
    ) -> Any:
        """Invoke execution via a named executor."""


__all__ = ["RuntimeBase"]
