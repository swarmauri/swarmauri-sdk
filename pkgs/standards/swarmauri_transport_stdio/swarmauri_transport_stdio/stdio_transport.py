from __future__ import annotations

import asyncio
import contextlib
from typing import Optional, Sequence

from swarmauri_base.transports.peer_mixin import PeerTransportMixin
from swarmauri_base.transports.runnable_mixin import RunnableMixin
from swarmauri_base.transports import TransportBase
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


class StdioTransport(
    TransportBase, RunnableMixin, PeerTransportMixin, UnicastTransportMixin
):
    """Spawned process transport that communicates over stdio."""

    def __init__(self, argv: Sequence[str]) -> None:
        super().__init__(name="STDIO")
        self._argv = list(argv)
        self._process: asyncio.Process | None = None

    def supports(self) -> TransportCapabilities:
        return TransportCapabilities(
            protocols=frozenset({Protocol.STDIO}),
            io=IOModel.STREAM,
            casts=frozenset({Cast.UNICAST}),
            features=frozenset({Feature.RELIABLE, Feature.ORDERED}),
            security=SecurityMode.NONE,
            schemes=frozenset({AddressScheme.STDIO}),
        )

    async def _start_server(self, **kwargs) -> None:
        raise NotImplementedError("STDIO transport launches child processes only")

    async def _open_client(self) -> None:
        self._process = await asyncio.create_subprocess_exec(
            *self._argv,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
        )

    async def _close_client(self) -> None:
        if self._process is not None:
            self._process.terminate()
            with contextlib.suppress(Exception):
                await self._process.wait()
            self._process = None

    async def send(
        self, target: str, data: bytes, *, timeout: Optional[float] = None
    ) -> None:
        if self._process is None or self._process.stdin is None:
            raise RuntimeError("not connected")
        self._process.stdin.write(data)
        await asyncio.wait_for(self._process.stdin.drain(), timeout)

    async def recv(self, *, timeout: Optional[float] = None) -> bytes:
        if self._process is None or self._process.stdout is None:
            raise RuntimeError("not connected")
        return await asyncio.wait_for(self._process.stdout.read(65536), timeout)
