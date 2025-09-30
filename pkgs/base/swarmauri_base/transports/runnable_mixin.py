from __future__ import annotations

import asyncio
import inspect
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict

from .i_runnable import Handler, IRunnable, Role


class RunnableMixin(IRunnable, BaseModel):
    """Adds synchronous and asynchronous run helpers to a transport."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="ignore")

    async def _run_async(
        self,
        *,
        role: Role,
        handler: Handler | None = None,
        forever: bool = False,
        stop_event: Optional[asyncio.Event] = None,
        handler_kwargs: Optional[dict[str, Any]] = None,
        **ctx_kwargs: Any,
    ) -> None:
        handler = handler or (lambda *_args, **_kwargs: None)
        handler_kwargs = handler_kwargs or {}

        if role == "server":
            ctx = self.server(**ctx_kwargs)  # type: ignore[attr-defined]
        else:
            ctx = self.client(**ctx_kwargs)  # type: ignore[attr-defined]

        async with ctx:

            async def _invoke() -> None:
                result = handler(self, **handler_kwargs)
                if inspect.isawaitable(result):
                    await result

            if not forever:
                await _invoke()
                return

            event = stop_event or asyncio.Event()
            while not event.is_set():
                await _invoke()

    def run(
        self,
        *,
        role: Role,
        handler: Handler | None = None,
        forever: bool = False,
        stop_event: Optional[asyncio.Event] = None,
        handler_kwargs: Optional[dict[str, Any]] = None,
        **ctx_kwargs: Any,
    ) -> None:
        asyncio.run(
            self._run_async(
                role=role,
                handler=handler,
                forever=forever,
                stop_event=stop_event,
                handler_kwargs=handler_kwargs,
                **ctx_kwargs,
            )
        )
