"""WebSocket connection interface."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Iterator
from typing import Optional, TypeAlias

WebSocketMessage: TypeAlias = str | bytes


class IWebSocketConnection(ABC):
    connection_id: str
    state: str
    subprotocol: str | None

    @abstractmethod
    def send(self, message: WebSocketMessage) -> None: ...

    @abstractmethod
    async def asend(self, message: WebSocketMessage) -> None: ...

    @abstractmethod
    def receive(self) -> WebSocketMessage: ...

    @abstractmethod
    async def areceive(self) -> WebSocketMessage: ...

    @abstractmethod
    def iter_messages(self) -> Iterator[WebSocketMessage]: ...

    @abstractmethod
    def aiter_messages(self) -> AsyncIterator[WebSocketMessage]: ...

    @abstractmethod
    def ping(self, data: bytes = b"") -> None: ...

    @abstractmethod
    async def aping(self, data: bytes = b"") -> None: ...

    @abstractmethod
    def close(self, code: int = 1000, reason: str = "") -> None: ...

    @abstractmethod
    async def aclose(self, code: int = 1000, reason: str = "") -> None: ...
