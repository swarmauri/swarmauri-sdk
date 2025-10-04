from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Awaitable, Literal, Protocol

Role = Literal["server", "client"]


class Handler(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> Awaitable[None] | None: ...


class IRunnable(ABC):
    """Runnable transports can open server/client contexts and run a handler within them."""

    @abstractmethod
    async def _run_async(
        self,
        *,
        role: Role,
        handler: Handler,
        forever: bool = False,
        stop_event: Any | None = None,
        handler_kwargs: dict[str, Any] | None = None,
        **ctx_kwargs: Any,
    ) -> None: ...

    @abstractmethod
    def run(
        self,
        *,
        role: Role,
        handler: Handler,
        forever: bool = False,
        stop_event: Any | None = None,
        handler_kwargs: dict[str, Any] | None = None,
        **ctx_kwargs: Any,
    ) -> None: ...
