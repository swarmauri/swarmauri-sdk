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
        call_id: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> Any: ...

    @abstractmethod
    async def aexecute(
        self,
        tool: Any,
        arguments: Mapping[str, Any],
        *,
        call_id: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> Any: ...

    @abstractmethod
    def cancel(self, call_id: str) -> bool: ...

    @abstractmethod
    async def acancel(self, call_id: str) -> bool: ...
