import asyncio
from typing import Any

from pydantic import PrivateAttr

from swarmauri_base.transports.websocket.WebSocketConnectionBase import (
    WebSocketConnectionBase,
)
from swarmauri_base.transports.websocket.WebSocketState import WebSocketState
from swarmauri_core.transports.i_websocket_connection import WebSocketMessage


class WebSocketConnection(WebSocketConnectionBase):
    _sync_socket: Any = PrivateAttr(default=None)
    _async_socket: Any = PrivateAttr(default=None)

    @classmethod
    def from_sync(cls, socket: Any) -> "WebSocketConnection":
        result = cls(
            state=WebSocketState.OPEN.value,
            subprotocol=getattr(socket, "subprotocol", None),
        )
        result._sync_socket = socket
        return result

    @classmethod
    def from_async(cls, socket: Any) -> "WebSocketConnection":
        result = cls(
            state=WebSocketState.OPEN.value,
            subprotocol=getattr(socket, "subprotocol", None),
        )
        result._async_socket = socket
        return result

    def send(self, message: WebSocketMessage) -> None:
        if self._sync_socket is not None:
            self._sync_socket.send(message)
            return
        self._run_sync(self.asend(message))

    async def asend(self, message: WebSocketMessage) -> None:
        if self._async_socket is not None:
            await self._async_socket.send(message)
            return
        if self._sync_socket is None:
            raise RuntimeError("WebSocket is not connected")
        await asyncio.to_thread(self._sync_socket.send, message)

    def receive(self) -> WebSocketMessage:
        if self._sync_socket is not None:
            return self._sync_socket.recv()
        return self._run_sync(self.areceive())

    async def areceive(self) -> WebSocketMessage:
        if self._async_socket is not None:
            return await self._async_socket.recv()
        if self._sync_socket is None:
            raise RuntimeError("WebSocket is not connected")
        return await asyncio.to_thread(self._sync_socket.recv)

    def ping(self, data: bytes = b"") -> None:
        if self._sync_socket is not None:
            self._sync_socket.ping(data)
            return
        self._run_sync(self.aping(data))

    async def aping(self, data: bytes = b"") -> None:
        if self._async_socket is not None:
            waiter = await self._async_socket.ping(data)
            await waiter
            return
        if self._sync_socket is None:
            raise RuntimeError("WebSocket is not connected")
        await asyncio.to_thread(self._sync_socket.ping, data)

    def close(self, code: int = 1000, reason: str = "") -> None:
        if self.state == WebSocketState.CLOSED.value:
            return
        if self._sync_socket is not None:
            self._sync_socket.close(code=code, reason=reason)
            self.state = WebSocketState.CLOSED.value
            return
        self._run_sync(self.aclose(code, reason))

    async def aclose(self, code: int = 1000, reason: str = "") -> None:
        if self.state == WebSocketState.CLOSED.value:
            return
        self.state = WebSocketState.CLOSING.value
        if self._async_socket is not None:
            await self._async_socket.close(code=code, reason=reason)
        elif self._sync_socket is not None:
            await asyncio.to_thread(
                self._sync_socket.close, code=code, reason=reason
            )
        self.state = WebSocketState.CLOSED.value
