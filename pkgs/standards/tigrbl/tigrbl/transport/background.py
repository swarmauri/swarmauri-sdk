"""Background task helpers with Starlette-compatible call behavior."""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class BackgroundTask:
    """Run a callable after response handling, matching Starlette semantics."""

    func: Callable[..., Any]
    args: tuple[Any, ...] = ()
    kwargs: dict[str, Any] | None = None

    def __init__(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        self.func = func
        self.args = args
        self.kwargs = kwargs

    async def __call__(self) -> None:
        result = self.func(*self.args, **(self.kwargs or {}))
        if inspect.isawaitable(result):
            await result


__all__ = ["BackgroundTask"]
