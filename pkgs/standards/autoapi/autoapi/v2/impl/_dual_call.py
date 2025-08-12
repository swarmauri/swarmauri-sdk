from __future__ import annotations

import asyncio
import functools
import anyio
from typing import Any, Awaitable, Callable, Coroutine, Generic, ParamSpec, TypeVar

P = ParamSpec("P")
T = TypeVar("T")


def in_event_loop() -> bool:
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return False
    return True


class CallableOp(Generic[P, T]):
    """Wrap an async operation for dual sync/async ergonomics."""

    def __init__(self, fn: Callable[P, Awaitable[T]]):
        self._fn = fn
        functools.update_wrapper(self, fn)

    async def _acall(self, *args: P.args, **kwargs: P.kwargs) -> T:
        return await self._fn(*args, **kwargs)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T | Coroutine[Any, Any, T]:
        if in_event_loop():
            return self._acall(*args, **kwargs)
        return anyio.run(lambda: self._acall(*args, **kwargs))

    def a(self, *args: P.args, **kwargs: P.kwargs) -> Coroutine[Any, Any, T]:
        return self._acall(*args, **kwargs)
