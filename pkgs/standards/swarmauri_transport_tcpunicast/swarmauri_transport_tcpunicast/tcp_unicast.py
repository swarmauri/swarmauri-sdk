from __future__ import annotations

import asyncio
import contextlib
from collections.abc import AsyncIterator

from swarmauri_base.transports.mixins import (
    PeerTransportMixin,
    UnicastTransportMixin,
)
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


class TCPUnicast(
    TransportBase, RunnableMixin, PeerTransportMixin, UnicastTransportMixin
):
    """Simple TCP client/server transport."""

    def __init__(self) -> None:
        super().__init__(name="TCP")
        self._server: asyncio.AbstractServer | None = None
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._accept_queue: asyncio.Queue[
            tuple[asyncio.StreamReader, asyncio.StreamWriter] | None
        ] = asyncio.Queue()

    def supports(self) -> TransportCapabilities:
        return TransportCapabilities(
            protocols=frozenset({Protocol.TCP}),
            io=IOModel.STREAM,
            casts=frozenset({Cast.UNICAST}),
            features=frozenset({Feature.RELIABLE, Feature.ORDERED}),
            security=SecurityMode.NONE,
            schemes=frozenset({AddressScheme.TCP}),
        )

    async def _start_server(
        self, host: str = "0.0.0.0", port: int = 9000
    ) -> None:
        self._accept_queue = queue = asyncio.Queue()

        def _accept(
            reader: asyncio.StreamReader, writer: asyncio.StreamWriter
        ) -> None:
            if queue is not self._accept_queue or self._server is None:
                writer.close()
                return
            if self._writer is not None and not self._writer.is_closing():
                writer.close()
                return
            self._reader = reader
            self._writer = writer
            queue.put_nowait((reader, writer))

        self._server = await asyncio.start_server(_accept, host, port)

    async def _stop_server(self) -> None:
        server, self._server = self._server, None
        if server is not None:
            server.close()
        queue = self._accept_queue
        while not queue.empty():
            streams = queue.get_nowait()
            if streams is not None:
                streams[1].close()
        # Each waiter passes this terminal marker to the next waiter. Keep the
        # old queue alive until its iterators finish, even after a restart.
        queue.put_nowait(None)
        try:
            await self._close_client()
        finally:
            if server is not None:
                await server.wait_closed()

    async def accept(
        self,
    ) -> AsyncIterator[tuple[asyncio.StreamReader, asyncio.StreamWriter]]:
        """Yield accepted streams while the server is running."""
        if self._server is None:
            raise RuntimeError("server not started")
        queue = self._accept_queue
        while True:
            streams = await queue.get()
            if streams is None:
                queue.put_nowait(None)
                return
            yield streams

    async def _open_client(
        self, host: str = "127.0.0.1", port: int = 9000
    ) -> None:
        self._reader, self._writer = await asyncio.open_connection(host, port)

    async def _close_client(self) -> None:
        if self._writer is not None:
            self._writer.close()
            with contextlib.suppress(Exception):
                await self._writer.wait_closed()
        self._reader = None
        self._writer = None

    async def send(
        self, target: str, data: bytes, *, timeout: float | None = None
    ) -> None:
        if self._writer is None:
            raise RuntimeError("not connected")
        self._writer.write(data)
        await asyncio.wait_for(self._writer.drain(), timeout)

    async def recv(self, *, timeout: float | None = None) -> bytes:
        if self._reader is None:
            raise RuntimeError("not connected")
        return await asyncio.wait_for(self._reader.read(65536), timeout)
