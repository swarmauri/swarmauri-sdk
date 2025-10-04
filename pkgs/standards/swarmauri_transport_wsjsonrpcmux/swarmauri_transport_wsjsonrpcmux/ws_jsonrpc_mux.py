from __future__ import annotations

import json
import ssl
from typing import Any, Awaitable, Callable, Optional

from swarmauri_base.transports.peer_mixin import PeerTransportMixin
from swarmauri_base.transports.runnable_mixin import RunnableMixin
from swarmauri_base.transports import TransportBase
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


class WsJsonrpcMuxTransport(TransportBase, RunnableMixin, PeerTransportMixin):
    """WebSocket transport that exchanges JSON-RPC 2.0 messages."""

    def __init__(self) -> None:
        super().__init__(name="WS-JSONRPC")
        self._server = None
        self._ws = None
        self._handler: Optional[RpcHandler] = None

    def set_rpc_handler(self, handler: RpcHandler) -> None:
        self._handler = handler

    def supports(self) -> TransportCapabilities:
        return TransportCapabilities(
            protocols=frozenset({Protocol.WS}),
            io=IOModel.STREAM,
            casts=frozenset({Cast.UNICAST}),
            features=frozenset({Feature.RELIABLE, Feature.ORDERED, Feature.MULTIPLEX}),
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
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "Install 'websockets' for WsJsonrpcMuxTransport"
            ) from exc

        async def _serve(ws):
            async for message in ws:
                request = json.loads(message)
                response: dict[str, Any] = {"jsonrpc": "2.0", "id": request.get("id")}
                try:
                    if self._handler is None:
                        raise RuntimeError("RPC handler not set")
                    result = await self._handler(
                        request.get("method"), request.get("params")
                    )
                    response["result"] = result
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
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "Install 'websockets' for WsJsonrpcMuxTransport"
            ) from exc
        self._ws = await websockets.connect(url, ssl=ssl_ctx)

    async def _close_client(self) -> None:
        if self._ws is not None:
            await self._ws.close()
            self._ws = None

    async def call(
        self, method: str, params: JSONValue = None, *, id: JSONValue = 1
    ) -> JSONValue:
        if self._ws is None:
            raise RuntimeError("not connected")
        payload = json.dumps(
            {"jsonrpc": "2.0", "method": method, "params": params, "id": id}
        )
        await self._ws.send(payload)
        response = json.loads(await self._ws.recv())
        if "error" in response:
            raise RuntimeError(response["error"])
        return response.get("result")
