from __future__ import annotations

import asyncio
import json
import ssl
from contextlib import suppress
from typing import Any, Awaitable, Callable, Optional

from swarmauri_base.transports.runnable_mixin import RunnableMixin
from swarmauri_base.transports.TransportBase import TransportBase
from swarmauri_core.transports.capabilities import TransportCapabilities
from swarmauri_core.transports.enums import (
    AddressScheme,
    Cast,
    Feature,
    IOModel,
    Protocol,
    SecurityMode,
)

JSONValue = Any
RpcHandler = Callable[[str, JSONValue], Awaitable[JSONValue]]


class WsJsonrpcTransport(TransportBase, RunnableMixin):
    """Correlated JSON-RPC 2.0 calls over one WebSocket connection."""

    def __init__(self) -> None:
        super().__init__(name="WS-JSONRPC")
        self._server = None
        self._ws = None
        self._handler: Optional[RpcHandler] = None
        self._pending: dict[JSONValue, asyncio.Future[dict[str, Any]]] = {}
        self._receiver_task: Optional[asyncio.Task[None]] = None
        self._send_lock = asyncio.Lock()
        self._next_id = 1

    def set_rpc_handler(self, handler: RpcHandler) -> None:
        self._handler = handler

    def supports(self) -> TransportCapabilities:
        return TransportCapabilities(
            protocols=frozenset({Protocol.WS}),
            io=IOModel.STREAM,
            casts=frozenset({Cast.UNICAST}),
            features=frozenset({Feature.RELIABLE, Feature.ORDERED}),
            security=SecurityMode.TLS,
            schemes=frozenset({AddressScheme.HTTPS}),
        )

    async def _start_server(
        self,
        host: str = "0.0.0.0",
        port: int = 8081,
        ssl_ctx: Optional[ssl.SSLContext] = None,
    ) -> None:
        try:
            import websockets
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(
                "Install 'websockets' for WsJsonrpcTransport"
            ) from exc

        async def _serve(ws):
            async for message in ws:
                request = json.loads(message)
                response: dict[str, Any] = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                }
                try:
                    if self._handler is None:
                        raise RuntimeError("RPC handler not set")
                    response["result"] = await self._handler(
                        request.get("method"), request.get("params")
                    )
                except Exception as exc:
                    response["error"] = {"code": -32000, "message": str(exc)}
                await ws.send(json.dumps(response))

        self._server = await websockets.serve(_serve, host, port, ssl=ssl_ctx)

    async def _stop_server(self) -> None:
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()
            self._server = None

    async def _open_client(
        self, url: str, ssl_ctx: Optional[ssl.SSLContext] = None
    ) -> None:
        try:
            import websockets
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(
                "Install 'websockets' for WsJsonrpcTransport"
            ) from exc
        self._ws = await websockets.connect(url, ssl=ssl_ctx)
        self._receiver_task = asyncio.create_task(self._receive_loop())

    async def _receive_loop(self) -> None:
        assert self._ws is not None
        try:
            async for message in self._ws:
                response = json.loads(message)
                future = self._pending.pop(response.get("id"), None)
                if future is not None and not future.done():
                    future.set_result(response)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            for future in self._pending.values():
                if not future.done():
                    future.set_exception(exc)
            self._pending.clear()

    async def _close_client(self) -> None:
        if self._receiver_task is not None:
            self._receiver_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._receiver_task
            self._receiver_task = None
        if self._ws is not None:
            await self._ws.close()
            self._ws = None

    async def call(
        self, method: str, params: JSONValue = None, *, id: JSONValue = None
    ) -> JSONValue:
        if self._ws is None:
            raise RuntimeError("not connected")
        if id is None:
            id = self._next_id
            self._next_id += 1
        loop = asyncio.get_running_loop()
        future: asyncio.Future[dict[str, Any]] = loop.create_future()
        if id in self._pending:
            raise ValueError(f"JSON-RPC id already pending: {id!r}")
        self._pending[id] = future
        payload = json.dumps(
            {"jsonrpc": "2.0", "method": method, "params": params, "id": id}
        )
        try:
            async with self._send_lock:
                await self._ws.send(payload)
            response = await future
        finally:
            self._pending.pop(id, None)
        if "error" in response:
            raise RuntimeError(response["error"])
        return response.get("result")


WsJsonrpcMuxTransport = WsJsonrpcTransport
