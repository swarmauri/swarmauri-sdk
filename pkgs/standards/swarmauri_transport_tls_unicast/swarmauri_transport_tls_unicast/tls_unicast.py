"""TLS (and optional mutual TLS) unicast transport implementation."""

from __future__ import annotations

import asyncio
import ssl
from typing import AsyncIterator, Optional, Tuple

from swarmauri_base.transports import (
    PeerTransportMixin,
    TransportBase,
    UnicastTransportMixin,
)
from swarmauri_core.transports import (
    AddressScheme,
    Cast,
    Feature,
    IOModel,
    Protocol,
    SecurityMode,
    TransportCapabilities,
)


class TlsUnicastTransport(TransportBase, PeerTransportMixin, UnicastTransportMixin):
    """TLS-secured unicast transport built on top of asyncio streams."""

    def __init__(self, ssl_ctx: ssl.SSLContext, sni: Optional[str] = None):
        super().__init__(name="TLS")
        self._ssl_ctx = ssl_ctx
        self._sni = sni
        self._server: asyncio.AbstractServer | None = None
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._accept_queue: asyncio.Queue[
            Tuple[asyncio.StreamReader, asyncio.StreamWriter]
        ] = asyncio.Queue()

    def supports(self) -> TransportCapabilities:
        security = (
            SecurityMode.MTLS
            if self._ssl_ctx.verify_mode == ssl.CERT_REQUIRED
            else SecurityMode.TLS
        )
        features = {
            Feature.RELIABLE,
            Feature.ORDERED,
            Feature.ENCRYPTED,
            Feature.AUTHENTICATED,
        }
        if security is SecurityMode.MTLS:
            features.add(Feature.MUTUAL_AUTH)
        return TransportCapabilities(
            protocols=frozenset({Protocol.TLS}),
            io=IOModel.STREAM,
            casts=frozenset({Cast.UNICAST}),
            features=frozenset(features),
            security=security,
            schemes=frozenset({AddressScheme.TLS}),
        )

    async def _start_server(self, host: str = "0.0.0.0", port: int = 8443) -> None:
        async def _handler(
            reader: asyncio.StreamReader, writer: asyncio.StreamWriter
        ) -> None:
            await self._accept_queue.put((reader, writer))

        self._server = await asyncio.start_server(
            _handler, host, port, ssl=self._ssl_ctx
        )

    async def _stop_server(self) -> None:
        if self._server:
            self._server.close()
            await self._server.wait_closed()
            self._server = None
        self._accept_queue = asyncio.Queue()

    async def _open_client(self, host: str = "127.0.0.1", port: int = 8443) -> None:
        self._reader, self._writer = await asyncio.open_connection(
            host, port, ssl=self._ssl_ctx, server_hostname=self._sni
        )

    async def _close_client(self) -> None:
        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()
        self._reader = None
        self._writer = None

    async def accept(
        self,
    ) -> AsyncIterator[Tuple[asyncio.StreamReader, asyncio.StreamWriter]]:
        if not self._server:
            raise RuntimeError("server not started")
        while True:
            reader, writer = await self._accept_queue.get()
            self._reader, self._writer = reader, writer
            yield reader, writer

    async def send(
        self, target: str, data: bytes, *, timeout: Optional[float] = None
    ) -> None:
        if not self._writer:
            raise RuntimeError("not connected")
        self._writer.write(data)
        await asyncio.wait_for(self._writer.drain(), timeout)

    async def recv(self, *, timeout: Optional[float] = None) -> bytes:
        if not self._reader:
            raise RuntimeError("not connected")
        return await asyncio.wait_for(self._reader.read(65536), timeout)
