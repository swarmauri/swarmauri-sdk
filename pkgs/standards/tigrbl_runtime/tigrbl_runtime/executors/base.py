from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ExecutorBase(ABC):
    """Contract for runtime executors."""

    def __init__(self, name: str) -> None:
        self.name = name

    def build(self, *args: Any, **kwargs: Any) -> Any:
        """Optional build hook for executor-specific precompiled callables."""
        del args, kwargs
        return None

    @abstractmethod
    async def invoke(
        self,
        *,
        runtime: Any,
        env: Any,
        ctx: Any,
        plan: Any,
        packed_plan: Any | None = None,
    ) -> Any:
        """Execute a kernel plan or packed kernel plan."""


__all__ = ["ExecutorBase"]
