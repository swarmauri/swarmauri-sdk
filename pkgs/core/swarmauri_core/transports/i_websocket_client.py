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
        headers: Optional[Mapping[str, str]] = None,
        subprotocols: Optional[Sequence[str]] = None,
        **kwargs: Any,
    ) -> IWebSocketConnection: ...

    @abstractmethod
    async def aconnect(
        self,
        url: str,
        *,
        headers: Optional[Mapping[str, str]] = None,
        subprotocols: Optional[Sequence[str]] = None,
        **kwargs: Any,
    ) -> IWebSocketConnection: ...
