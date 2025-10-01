from __future__ import annotations

import asyncio
import contextlib
import ssl
from typing import Optional

from swarmauri_base.transports.peer_mixin import PeerTransportMixin
from swarmauri_base.transports.runnable_mixin import RunnableMixin
from swarmauri_base.transports.transport_base import TransportBase
from swarmauri_base.transports.unicast_mixin import UnicastTransportMixin
from swarmauri_core.transports.capabilities import TransportCapabilities
from swarmauri_core.transports.enums import (
    AddressScheme,
    Cast,
    Feature,
    IOModel,
    Protocol,
    SecurityMode,
)


class MTLSUnicast(
    TransportBase, RunnableMixin, PeerTransportMixin, UnicastTransportMixin
):
    """Mutual TLS secured TCP transport."""

    def __init__(self, ssl_ctx: ssl.SSLContext) -> None:
        super().__init__(name="mTLS")
        self._ssl_ctx = ssl_ctx
        self._server: asyncio.AbstractServer | None = None
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None

    def supports(self) -> TransportCapabilities:
        return TransportCapabilities(
            protocols=frozenset({Protocol.MTLS}),
            io=IOModel.STREAM,
            casts=frozenset({Cast.UNICAST}),
            features=frozenset(
                {
                    Feature.RELIABLE,
                    Feature.ORDERED,
                    Feature.ENCRYPTED,
                    Feature.AUTHENTICATED,
                    Feature.MUTUAL_AUTH,
                }
            ),
            security=SecurityMode.MTLS,
            schemes=frozenset({AddressScheme.MTLS}),
        )

    async def _start_server(self, host: str = "0.0.0.0", port: int = 9443) -> None:
        with contextlib.suppress(Exception):
            self._ssl_ctx.set_alpn_protocols(["h2", "http/1.1"])

        async def _accept(
            reader: asyncio.StreamReader, writer: asyncio.StreamWriter
        ) -> None:
            self._reader = reader
            self._writer = writer
            await asyncio.Event().wait()

        self._server = await asyncio.start_server(
            _accept, host, port, ssl=self._ssl_ctx
        )

    async def _stop_server(self) -> None:
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()
            self._server = None

    async def _open_client(
        self,
        host: str = "127.0.0.1",
        port: int = 9443,
        server_hostname: Optional[str] = "localhost",
    ) -> None:
        with contextlib.suppress(Exception):
            self._ssl_ctx.set_alpn_protocols(["h2", "http/1.1"])
        self._reader, self._writer = await asyncio.open_connection(
            host,
            port,
            ssl=self._ssl_ctx,
            server_hostname=server_hostname,
        )

    async def _close_client(self) -> None:
        if self._writer is not None:
            self._writer.close()
            with contextlib.suppress(Exception):
                await self._writer.wait_closed()
        self._reader = None
        self._writer = None

    async def send(
        self, target: str, data: bytes, *, timeout: Optional[float] = None
    ) -> None:
        if self._writer is None:
            raise RuntimeError("not connected")
        self._writer.write(data)
        await asyncio.wait_for(self._writer.drain(), timeout)

    async def recv(self, *, timeout: Optional[float] = None) -> bytes:
        if self._reader is None:
            raise RuntimeError("not connected")
        return await asyncio.wait_for(self._reader.read(65536), timeout)
