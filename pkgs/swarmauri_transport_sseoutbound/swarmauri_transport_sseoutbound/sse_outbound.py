from __future__ import annotations

import asyncio
import contextlib
import ssl
from typing import Optional, Set

from swarmauri_base.transports.runnable_mixin import RunnableMixin
from swarmauri_base.transports.transport_base import TransportBase
from swarmauri_core.transports.capabilities import TransportCapabilities
from swarmauri_core.transports.enums import (
    AddressScheme,
    Cast,
    Feature,
    IOModel,
    Protocol,
    SecurityMode,
)


class SSEOutboundTransport(TransportBase, RunnableMixin):
    """Server-Sent Events transport for broadcasting data to clients."""

    def __init__(self) -> None:
        super().__init__(name="SSE")
        self._server: asyncio.AbstractServer | None = None
        self._clients: Set[asyncio.StreamWriter] = set()

    def supports(self) -> TransportCapabilities:
        return TransportCapabilities(
            protocols=frozenset({Protocol.HTTP1, Protocol.H2}),
            io=IOModel.STREAM,
            casts=frozenset({Cast.BROADCAST}),
            features=frozenset({Feature.RELIABLE, Feature.ORDERED}),
            security=SecurityMode.TLS,
            schemes=frozenset({AddressScheme.HTTP, AddressScheme.HTTPS}),
        )

    async def _start_server(
        self,
        host: str = "0.0.0.0",
        port: int = 8082,
        ssl_ctx: Optional[ssl.SSLContext] = None,
    ) -> None:
        async def _handler(
            reader: asyncio.StreamReader, writer: asyncio.StreamWriter
        ) -> None:
            writer.write(
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: text/event-stream\r\n"
                b"Cache-Control: no-cache\r\n\r\n"
            )
            await writer.drain()
            self._clients.add(writer)
            try:
                await asyncio.Event().wait()
            finally:
                self._clients.discard(writer)
                writer.close()
                with contextlib.suppress(Exception):
                    await writer.wait_closed()

        self._server = await asyncio.start_server(_handler, host, port, ssl=ssl_ctx)

    async def _stop_server(self) -> None:
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()
            self._server = None

    async def _open_client(self, **kwargs) -> None:
        raise NotImplementedError("SSE transport is server-only")

    async def _close_client(self) -> None:
        return None

    async def broadcast(self, data: bytes) -> None:
        frame = b"data: " + data + b"\n\n"
        dead: list[asyncio.StreamWriter] = []
        for writer in list(self._clients):
            try:
                writer.write(frame)
                await writer.drain()
            except Exception:
                dead.append(writer)
        for writer in dead:
            self._clients.discard(writer)
