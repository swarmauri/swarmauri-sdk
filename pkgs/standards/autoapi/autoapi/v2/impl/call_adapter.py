from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable, Coroutine, Generic, TypeVar

import anyio

T = TypeVar("T")


def in_event_loop() -> bool:
    """Return ``True`` if an event loop is currently running."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return False
    return True


class OpCall(Generic[T]):
    """Wrap an async callable for dual sync/async ergonomics."""

    def __init__(self, acall: Callable[..., Awaitable[T]]):
        self._acall = acall

    def __call__(self, *args: Any, **kw: Any) -> T | Coroutine[Any, Any, T]:
        if in_event_loop():
            return self._acall(*args, **kw)
        return anyio.run(self._acall, *args, **kw)

    def a(self, *args: Any, **kw: Any) -> Awaitable[T]:
        return self._acall(*args, **kw)
