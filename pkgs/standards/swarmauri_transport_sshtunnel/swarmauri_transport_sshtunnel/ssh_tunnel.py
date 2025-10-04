from __future__ import annotations

import asyncio
import contextlib
from typing import Optional, Tuple

from swarmauri_base.transports.peer_mixin import PeerTransportMixin
from swarmauri_base.transports.runnable_mixin import RunnableMixin
from swarmauri_base.transports.TransportBase import TransportBase
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


class SSHTunnelTransport(
    TransportBase, RunnableMixin, PeerTransportMixin, UnicastTransportMixin
):
    """Client transport that tunnels TCP traffic through an SSH process."""

    def __init__(
        self,
        jump_host: str,
        dest_host: str,
        dest_port: int,
        identity_file: Optional[str] = None,
    ) -> None:
        super().__init__(name="SSH-Tunnel")
        self._jump_host = jump_host
        self._destination: Tuple[str, int] = (dest_host, dest_port)
        self._identity_file = identity_file
        self._process: asyncio.Process | None = None

    def supports(self) -> TransportCapabilities:
        return TransportCapabilities(
            protocols=frozenset({Protocol.TCP}),
            io=IOModel.STREAM,
            casts=frozenset({Cast.UNICAST}),
            features=frozenset(
                {
                    Feature.RELIABLE,
                    Feature.ORDERED,
                    Feature.ENCRYPTED,
                    Feature.AUTHENTICATED,
                }
            ),
            security=SecurityMode.SSH,
            schemes=frozenset({AddressScheme.TCP}),
        )

    async def _start_server(self, **kwargs) -> None:
        raise NotImplementedError("SSH tunnel acts as a client")

    async def _open_client(self) -> None:
        args = [
            "ssh",
            "-o",
            "ExitOnForwardFailure=yes",
            "-W",
            f"{self._destination[0]}:{self._destination[1]}",
            self._jump_host,
        ]
        if self._identity_file:
            args[1:1] = ["-i", self._identity_file]
        self._process = await asyncio.create_subprocess_exec(
            *args,
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
