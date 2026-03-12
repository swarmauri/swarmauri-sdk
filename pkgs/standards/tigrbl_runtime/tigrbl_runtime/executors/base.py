from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar


class ExecutorBase(ABC):
    """Contract for runtime executors."""

    name: ClassVar[str]

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
