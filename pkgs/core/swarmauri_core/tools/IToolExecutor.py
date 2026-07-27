"""Tool execution interface."""

from abc import ABC, abstractmethod
from typing import Any, Mapping, Optional


class IToolExecutor(ABC):
    @abstractmethod
    def execute(
        self,
        tool: Any,
        arguments: Mapping[str, Any],
        *,
        call_id: str | None = None,
        timeout: float | None = None,
        context: Mapping[str, Any] | None = None,
    ) -> Any: ...

    @abstractmethod
    async def aexecute(
        self,
        tool: Any,
        arguments: Mapping[str, Any],
        *,
        call_id: str | None = None,
        timeout: float | None = None,
        context: Mapping[str, Any] | None = None,
    ) -> Any: ...

    @abstractmethod
    def cancel(self, call_id: str) -> bool: ...

    @abstractmethod
    async def acancel(self, call_id: str) -> bool: ...
