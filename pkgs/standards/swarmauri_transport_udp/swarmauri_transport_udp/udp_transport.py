"""UDP transport supporting unicast, broadcast, multicast, and anycast."""

from __future__ import annotations

import asyncio
import socket
from typing import Optional, Sequence

from swarmauri_base.transports import (
    AnycastTransportMixin,
    BroadcastTransportMixin,
    MulticastTransportMixin,
    TransportBase,
    UnicastTransportMixin,
)
from swarmauri_core.transports import (
    AddressScheme,
    Cast,
    IOModel,
    Protocol,
    SecurityMode,
    TransportCapabilities,
)


class UdpTransport(
    TransportBase,
    UnicastTransportMixin,
    MulticastTransportMixin,
    BroadcastTransportMixin,
    AnycastTransportMixin,
):
    """Datagram transport built on UDP sockets."""

    def __init__(
        self, bind: Optional[str] = None, multicast_groups: Sequence[str] = ()
    ):  # noqa: B008
        super().__init__(name="UDP")
        self._bind = bind
        self._groups = tuple(multicast_groups)
        self._sock: Optional[socket.socket] = None
        self._loop = asyncio.get_event_loop()

    def supports(self) -> TransportCapabilities:
        return TransportCapabilities(
            protocols=frozenset({Protocol.UDP}),
            io=IOModel.DATAGRAM,
            casts=frozenset(
                {Cast.UNICAST, Cast.BROADCAST, Cast.MULTICAST, Cast.ANYCAST}
            ),
            features=frozenset(),
            security=SecurityMode.NONE,
            schemes=frozenset({AddressScheme.UDP}),
        )

    async def _start_server(self) -> None:
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        host, port = (self._bind or "0.0.0.0:5000").split(":", 1)
        self._sock.bind((host, int(port)))
        for group in self._groups:
            mreq = socket.inet_aton(group.split(":", 1)[0]) + socket.inet_aton(
                "0.0.0.0"
            )
            self._sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self._sock.setblocking(False)

    async def _stop_server(self) -> None:
        if self._sock:
            self._sock.close()
            self._sock = None

    async def _open_client(self) -> None:
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setblocking(False)

    async def _close_client(self) -> None:
        if self._sock:
            self._sock.close()
            self._sock = None

    async def send(
        self, target: str, data: bytes, *, timeout: Optional[float] = None
    ) -> None:
        if not self._sock:
            raise RuntimeError("socket not initialized")
        host, port = target.split(":", 1)
        self._sock.sendto(data, (host, int(port)))

    async def recv(self, *, timeout: Optional[float] = None) -> bytes:
        if not self._sock:
            raise RuntimeError("socket not initialized")
        fut = self._loop.run_in_executor(None, self._sock.recv, 65536)
        return await asyncio.wait_for(fut, timeout)

    async def broadcast(self, data: bytes, *, timeout: Optional[float] = None) -> None:
        if not self._sock:
            raise RuntimeError("socket not initialized")
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        port = self._sock.getsockname()[1]
        self._sock.sendto(data, ("255.255.255.255", port))

    async def multicast(
        self, group: Sequence[str], data: bytes, *, timeout: Optional[float] = None
    ) -> None:
        if not self._sock:
            raise RuntimeError("socket not initialized")
        for address in group:
            host, port = address.split(":", 1)
            self._sock.sendto(data, (host, int(port)))

    async def anycast(
        self, candidates: Sequence[str], data: bytes, *, timeout: Optional[float] = None
    ) -> str:
        if not self._sock:
            raise RuntimeError("socket not initialized")
        for candidate in candidates:
            host, port = candidate.split(":", 1)
            self._sock.sendto(data, (host, int(port)))
            return candidate
        raise RuntimeError("no candidates provided")
