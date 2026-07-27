"""Shared WebSocket connection lifecycle."""

import asyncio
from abc import abstractmethod
from collections.abc import AsyncIterator, Iterator
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from swarmauri_core.transports.i_websocket_connection import (
    IWebSocketConnection,
    WebSocketMessage,
)

from .WebSocketState import WebSocketState


class WebSocketConnectionBase(IWebSocketConnection, BaseModel):
    connection_id: str = Field(default_factory=lambda: str(uuid4()))
    state: str = WebSocketState.NEW.value
    subprotocol: Optional[str] = None
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    @staticmethod
    def _run_sync(awaitable: Any) -> Any:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(awaitable)
        raise RuntimeError("Use the async WebSocket API inside an event loop")

    def send(self, message: WebSocketMessage) -> None:
        self._run_sync(self.asend(message))

    @abstractmethod
    async def asend(self, message: WebSocketMessage) -> None: ...

    def receive(self) -> WebSocketMessage:
        return self._run_sync(self.areceive())

    @abstractmethod
    async def areceive(self) -> WebSocketMessage: ...

    def iter_messages(self) -> Iterator[WebSocketMessage]:
        while self.state == WebSocketState.OPEN.value:
            yield self.receive()

    async def aiter_messages(self) -> AsyncIterator[WebSocketMessage]:
        while self.state == WebSocketState.OPEN.value:
            yield await self.areceive()

    def ping(self, data: bytes = b"") -> None:
        self._run_sync(self.aping(data))

    @abstractmethod
    async def aping(self, data: bytes = b"") -> None: ...

    def close(self, code: int = 1000, reason: str = "") -> None:
        self._run_sync(self.aclose(code, reason))

    @abstractmethod
    async def aclose(self, code: int = 1000, reason: str = "") -> None: ...
