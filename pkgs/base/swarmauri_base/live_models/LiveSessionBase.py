"""Reusable asynchronous live-session lifecycle and event delivery."""

import asyncio
from abc import abstractmethod
from collections.abc import AsyncIterator, Iterator
from typing import Any, Literal
from uuid import uuid4

from pydantic import ConfigDict, Field, PrivateAttr
from swarmauri_core.live_models.ILiveInput import ILiveInput
from swarmauri_core.live_models.ILiveSession import ILiveSession

from swarmauri_base.ComponentBase import ComponentBase

from .LiveEventBase import LiveEventBase
from .LiveSessionState import LiveSessionState


class LiveSessionBase(ILiveSession, ComponentBase):
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    state: str = LiveSessionState.NEW.value
    terminal_error: Any = Field(default=None, exclude=True)
    type: Literal["LiveSessionBase"] = "LiveSessionBase"
    resource: Literal["LiveSession"] = "LiveSession"
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    _events: asyncio.Queue[LiveEventBase | None] = PrivateAttr(
        default_factory=asyncio.Queue
    )
    _closed_event: asyncio.Event = PrivateAttr(default_factory=asyncio.Event)
    _finish_lock: asyncio.Lock = PrivateAttr(default_factory=asyncio.Lock)
    _terminal_signalled: bool = PrivateAttr(default=False)

    def mark_open(self) -> None:
        self.state = LiveSessionState.OPEN.value

    async def emit(self, event: LiveEventBase) -> None:
        if not self._terminal_signalled:
            await self._events.put(event)

    async def finish(self) -> None:
        await self._finish(LiveSessionState.CLOSED, None)

    async def fail(self, error: BaseException) -> None:
        await self._finish(LiveSessionState.FAILED, error)

    async def _finish(
        self,
        state: LiveSessionState,
        error: BaseException | None,
    ) -> None:
        async with self._finish_lock:
            if self._terminal_signalled:
                return
            self._terminal_signalled = True
            self.terminal_error = error
            self.state = state.value
            await self._events.put(None)
            self._closed_event.set()

    def send(self, input_data: ILiveInput) -> None:
        raise RuntimeError("Use LiveModel.connect() for synchronous live APIs")

    async def asend(self, input_data: ILiveInput) -> None:
        if self.state != LiveSessionState.OPEN.value:
            raise RuntimeError(f"Live session is not open: {self.state}")
        await self._asend_impl(input_data)

    @abstractmethod
    async def _asend_impl(self, input_data: ILiveInput) -> None: ...

    def stream(self) -> Iterator[LiveEventBase]:
        raise RuntimeError("Use LiveModel.connect() for synchronous live APIs")
        yield  # pragma: no cover

    async def astream(self) -> AsyncIterator[LiveEventBase]:
        while True:
            event = await self._events.get()
            if event is None:
                return
            yield event

    def wait_closed(self) -> None:
        raise RuntimeError("Use LiveModel.connect() for synchronous live APIs")

    async def await_closed(self) -> None:
        await self._closed_event.wait()

    def close(self) -> None:
        raise RuntimeError("Use LiveModel.connect() for synchronous live APIs")

    async def aclose(self) -> None:
        if self._terminal_signalled:
            return
        self.state = LiveSessionState.CLOSING.value
        try:
            await self._aclose_impl()
        except Exception as exc:
            await self.fail(exc)
            raise
        else:
            await self.finish()

    @abstractmethod
    async def _aclose_impl(self) -> None: ...

    async def __aenter__(self) -> "LiveSessionBase":
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()
