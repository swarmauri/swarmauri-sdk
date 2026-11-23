from collections.abc import Mapping, Sequence
from typing import Any

from swarmauri_base.transports.websocket.WebSocketClientBase import (
    WebSocketClientBase,
)

from .WebSocketConnection import WebSocketConnection


class WebSocketClient(WebSocketClientBase):
    def connect(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        subprotocols: Sequence[str] | None = None,
        **kwargs: Any,
    ) -> WebSocketConnection:
        from websockets.sync.client import connect

        socket = connect(
            url,
            additional_headers=dict(headers or {}),
            subprotocols=list(subprotocols or []),
            open_timeout=self.timeout,
            **kwargs,
        )
        return WebSocketConnection.from_sync(socket)

    async def aconnect(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        subprotocols: Sequence[str] | None = None,
        **kwargs: Any,
    ) -> WebSocketConnection:
        from websockets.asyncio.client import connect

        socket = await connect(
            url,
            additional_headers=dict(headers or {}),
            subprotocols=list(subprotocols or []),
            open_timeout=self.timeout,
            ping_interval=self.ping_interval,
            **kwargs,
        )
        return WebSocketConnection.from_async(socket)
