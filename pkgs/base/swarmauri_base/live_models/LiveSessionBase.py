"""Reusable live-session lifecycle and event delivery."""

import asyncio
from abc import abstractmethod
from collections.abc import AsyncIterator, Iterator
from typing import Any, Literal
from uuid import uuid4

from pydantic import ConfigDict, Field, PrivateAttr

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.live_models.ILiveInput import ILiveInput
from swarmauri_core.live_models.ILiveSession import ILiveSession

from .LiveEventBase import LiveEventBase
from .LiveSessionState import LiveSessionState


class LiveSessionBase(ILiveSession, ComponentBase):
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    state: str = LiveSessionState.NEW.value
    type: Literal["LiveSessionBase"] = "LiveSessionBase"

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")
    _events: asyncio.Queue[LiveEventBase | None] = PrivateAttr(
        default_factory=asyncio.Queue
    )

    @staticmethod
    def _run_sync(awaitable: Any) -> Any:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(awaitable)
        raise RuntimeError(
            "Synchronous live APIs cannot run inside an active event loop; "
            "use the async method instead."
        )

    def mark_open(self) -> None:
        self.state = LiveSessionState.OPEN.value

    async def emit(self, event: LiveEventBase) -> None:
        await self._events.put(event)

    def send(self, input_data: ILiveInput) -> None:
        self._run_sync(self.asend(input_data))

    async def asend(self, input_data: ILiveInput) -> None:
        if self.state != LiveSessionState.OPEN.value:
            raise RuntimeError(f"Live session is not open: {self.state}")
        await self._asend_impl(input_data)

    @abstractmethod
    async def _asend_impl(self, input_data: ILiveInput) -> None: ...

    def stream(self) -> Iterator[LiveEventBase]:
        while True:
            event = self._run_sync(self._events.get())
            if event is None:
                return
            yield event

    async def astream(self) -> AsyncIterator[LiveEventBase]:
        while True:
            event = await self._events.get()
            if event is None:
                return
            yield event

    def close(self) -> None:
        self._run_sync(self.aclose())

    async def aclose(self) -> None:
        if self.state in {
            LiveSessionState.CLOSING.value,
            LiveSessionState.CLOSED.value,
        }:
            return
        self.state = LiveSessionState.CLOSING.value
        try:
            await self._aclose_impl()
        finally:
            self.state = LiveSessionState.CLOSED.value
            await self._events.put(None)

    @abstractmethod
    async def _aclose_impl(self) -> None: ...

    def __enter__(self) -> "LiveSessionBase":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    async def __aenter__(self) -> "LiveSessionBase":
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.aclose()
