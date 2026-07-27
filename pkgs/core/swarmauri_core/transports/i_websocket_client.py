"""WebSocket client interface."""

from abc import ABC, abstractmethod
from typing import Any, Mapping, Optional, Sequence

from .i_websocket_connection import IWebSocketConnection


class IWebSocketClient(ABC):
    @abstractmethod
    def connect(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        subprotocols: Sequence[str] | None = None,
        **kwargs: Any,
    ) -> IWebSocketConnection: ...

    @abstractmethod
    async def aconnect(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        subprotocols: Sequence[str] | None = None,
        **kwargs: Any,
    ) -> IWebSocketConnection: ...
