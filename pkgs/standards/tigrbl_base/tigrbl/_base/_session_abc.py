from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable


class SessionABC(ABC):
    """Authoritative Tigrbl session interface."""

    @abstractmethod
    async def begin(self) -> None: ...

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...

    @abstractmethod
    def in_transaction(self) -> bool: ...

    @abstractmethod
    async def get(self, model: type, ident: Any) -> Any | None: ...

    @abstractmethod
    def add(self, obj: Any) -> None: ...

    @abstractmethod
    async def delete(self, obj: Any) -> None: ...

    @abstractmethod
    async def flush(self) -> None: ...

    @abstractmethod
    async def refresh(self, obj: Any) -> None: ...

    @abstractmethod
    async def execute(self, stmt: Any) -> Any: ...

    @abstractmethod
    async def close(self) -> None: ...

    @abstractmethod
    async def run_sync(self, fn: Callable[[Any], Any]) -> Any: ...


__all__ = ["SessionABC"]
