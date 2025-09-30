"""Unix domain socket transport providing unicast peer communication."""

from __future__ import annotations

import asyncio
import os
from typing import Optional

from swarmauri_core.transports import (
    AddressScheme,
    Cast,
    Feature,
    IOModel,
    PeerTransportMixin,
    Protocol,
    SecurityMode,
    TransportBase,
    TransportCapabilities,
    UnicastTransportMixin,
)


class UdsUnicastTransport(TransportBase, UnicastTransportMixin, PeerTransportMixin):
    """Unix domain socket transport supporting unicast messaging."""

    def __init__(self, path: str):
        super().__init__(name=f"UDS:{path}")
        self._path = path
        self._server: asyncio.AbstractServer | None = None
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None

    def supports(self) -> TransportCapabilities:
        return TransportCapabilities(
            protocols=frozenset({Protocol.UDS}),
            io=IOModel.STREAM,
            casts=frozenset({Cast.UNICAST}),
            features=frozenset({Feature.RELIABLE, Feature.ORDERED, Feature.LOCAL_ONLY}),
            security=SecurityMode.NONE,
            schemes=frozenset({AddressScheme.UDS}),
        )

    async def _start_server(self) -> None:
        if os.path.exists(self._path):
            os.unlink(self._path)
        self._server = await asyncio.start_unix_server(self._on_client, path=self._path)

    async def _stop_server(self) -> None:
        if self._server:
            self._server.close()
            await self._server.wait_closed()
            self._server = None
        try:
            os.unlink(self._path)
        except FileNotFoundError:
            pass

    async def _open_client(self) -> None:
        self._reader, self._writer = await asyncio.open_unix_connection(self._path)

    async def _close_client(self) -> None:
        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()
        self._reader = None
        self._writer = None

    async def accept(self):
        if not self._server:
            raise RuntimeError("server not started")
        while True:
            await asyncio.sleep(3600)

    async def _on_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        self._reader, self._writer = reader, writer

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
