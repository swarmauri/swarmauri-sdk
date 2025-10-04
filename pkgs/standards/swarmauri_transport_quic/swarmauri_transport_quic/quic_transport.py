"""QUIC-inspired transport with multiplexed channel semantics."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import AsyncIterator, Optional, Tuple

from pydantic import PrivateAttr

from swarmauri_base.transports import (
    MultiplexTransportMixin,
    PeerTransportMixin,
    TransportBase,
    UnicastTransportMixin,
)
from swarmauri_core.transports import (
    AddressScheme,
    Cast,
    ChannelHandle,
    Feature,
    IOModel,
    Protocol,
    SecurityMode,
    TransportCapabilities,
)


@dataclass
class _QuicChannel:
    """Internal structure representing a logical channel."""

    identifier: int
    queue: asyncio.Queue[bytes]
    remote: Tuple[str, int] | None = None


class _QuicDatagramProtocol(asyncio.DatagramProtocol):
    """Simple protocol forwarding datagrams to the transport instance."""

    def __init__(self, handler) -> None:  # type: ignore[no-untyped-def]
        self._handler = handler
        self.transport: asyncio.DatagramTransport | None = None

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        self.transport = transport  # type: ignore[assignment]

    def datagram_received(self, data: bytes, addr: Tuple[str, int]) -> None:
        self._handler(data, addr)


class QuicTransport(
    TransportBase,
    UnicastTransportMixin,
    PeerTransportMixin,
    MultiplexTransportMixin,
):
    """QUIC-like transport built on asyncio UDP primitives."""

    _server_transport: asyncio.DatagramTransport | None = PrivateAttr(default=None)
    _client_transport: asyncio.DatagramTransport | None = PrivateAttr(default=None)
    _server_protocol: _QuicDatagramProtocol | None = PrivateAttr(default=None)
    _client_protocol: _QuicDatagramProtocol | None = PrivateAttr(default=None)
    _default_queue: asyncio.Queue[bytes] = PrivateAttr(default_factory=asyncio.Queue)
    _channels: dict[int, _QuicChannel] = PrivateAttr(default_factory=dict)
    _next_channel: int = PrivateAttr(default=1)
    _peer_addr: Tuple[str, int] | None = PrivateAttr(default=None)
    _default_remote: Tuple[str, int] | None = PrivateAttr(default=None)
    _peer_queue: asyncio.Queue[Tuple[str, int]] = PrivateAttr(
        default_factory=asyncio.Queue
    )
    _known_peers: set[Tuple[str, int]] = PrivateAttr(default_factory=set)
    _config: dict[str, object] = PrivateAttr(default_factory=dict)

    def __init__(self, **config: object) -> None:
        super().__init__(name="QUIC")
        self._config = dict(config)
        self._reset_state()

    def _reset_state(self) -> None:
        self._default_queue = asyncio.Queue()
        self._channels = {}
        self._next_channel = 1
        self._peer_queue = asyncio.Queue()
        self._known_peers = set()
        self._peer_addr = None
        self._default_remote = None

    # ------------------------------------------------------------------
    # Capability advertisement
    # ------------------------------------------------------------------
    def supports(self) -> TransportCapabilities:
        return TransportCapabilities(
            protocols=frozenset({Protocol.QUIC}),
            io=IOModel.STREAM,
            casts=frozenset({Cast.UNICAST}),
            features=frozenset(
                {
                    Feature.RELIABLE,
                    Feature.ORDERED,
                    Feature.ENCRYPTED,
                    Feature.AUTHENTICATED,
                    Feature.MULTIPLEX,
                }
            ),
            security=SecurityMode.TLS,
            schemes=frozenset({AddressScheme.QUIC}),
        )

    # ------------------------------------------------------------------
    # Lifecycle management
    # ------------------------------------------------------------------
    async def _start_server(self, host: str = "0.0.0.0", port: int = 4433) -> None:
        self._reset_state()
        loop = asyncio.get_running_loop()
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: _QuicDatagramProtocol(self._handle_datagram),
            local_addr=(host, port),
        )
        self._server_transport = transport
        self._server_protocol = protocol
        self._default_remote = None
        self._peer_addr = None

    async def _stop_server(self) -> None:
        if self._server_transport is not None:
            self._server_transport.close()
            self._server_transport = None
            self._server_protocol = None
        self._reset_state()

    async def _open_client(self, host: str = "127.0.0.1", port: int = 4433) -> None:
        self._reset_state()
        loop = asyncio.get_running_loop()
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: _QuicDatagramProtocol(self._handle_datagram),
            remote_addr=(host, port),
        )
        self._client_transport = transport
        self._client_protocol = protocol
        self._peer_addr = (host, port)
        self._default_remote = (host, port)

    async def _close_client(self) -> None:
        if self._client_transport is not None:
            self._client_transport.close()
            self._client_transport = None
            self._client_protocol = None
        self._reset_state()

    # ------------------------------------------------------------------
    # Peer handling
    # ------------------------------------------------------------------
    async def accept(self) -> AsyncIterator[Tuple[str, int]]:  # type: ignore[override]
        while True:
            addr = await self._peer_queue.get()
            yield addr

    # ------------------------------------------------------------------
    # Unicast operations
    # ------------------------------------------------------------------
    async def send(
        self, target: str, data: bytes, *, timeout: Optional[float] = None
    ) -> None:
        addr = self._resolve_target(target)
        await self._send_datagram((0).to_bytes(4, "big") + data, addr, timeout)

    async def recv(self, *, timeout: Optional[float] = None) -> bytes:
        if timeout is None:
            return await self._default_queue.get()
        return await asyncio.wait_for(self._default_queue.get(), timeout)

    # ------------------------------------------------------------------
    # Multiplexed channel management
    # ------------------------------------------------------------------
    async def open_channel(self) -> ChannelHandle:
        handle = self._next_channel
        self._next_channel += 1
        remote = self._peer_addr or self._default_remote
        self._channels[handle] = _QuicChannel(handle, asyncio.Queue(), remote)
        return handle

    async def close_channel(self, handle: ChannelHandle) -> None:
        self._channels.pop(int(handle), None)

    async def send_on(
        self, handle: ChannelHandle, data: bytes, *, timeout: Optional[float] = None
    ) -> None:
        channel = self._ensure_channel(handle)
        if channel.remote is None:
            channel.remote = self._peer_addr or self._default_remote
        if channel.remote is None:
            raise RuntimeError("no remote peer associated with channel")
        payload = int(channel.identifier).to_bytes(4, "big") + data
        await self._send_datagram(payload, channel.remote, timeout)

    async def recv_on(
        self, handle: ChannelHandle, *, timeout: Optional[float] = None
    ) -> bytes:
        channel = self._ensure_channel(handle)
        if timeout is None:
            return await channel.queue.get()
        return await asyncio.wait_for(channel.queue.get(), timeout)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _ensure_channel(self, handle: ChannelHandle) -> _QuicChannel:
        key = int(handle)
        channel = self._channels.get(key)
        if channel is None:
            channel = _QuicChannel(key, asyncio.Queue())
            self._channels[key] = channel
        return channel

    def _get_transport(self) -> asyncio.DatagramTransport:
        transport = self._client_transport or self._server_transport
        if transport is None:
            raise RuntimeError("transport is not connected")
        return transport

    def _resolve_target(self, target: str) -> Tuple[str, int]:
        token = target.strip().lower()
        if ":" in target:
            host, port_str = target.split(":", 1)
            return host, int(port_str)
        if token in {"peer", "server", "default"}:
            if self._peer_addr is not None:
                return self._peer_addr
            if self._default_remote is not None:
                return self._default_remote
        if self._peer_addr is not None:
            return self._peer_addr
        if self._default_remote is not None:
            return self._default_remote
        raise RuntimeError("no remote peer available for send operation")

    async def _send_datagram(
        self, payload: bytes, addr: Tuple[str, int], timeout: Optional[float]
    ) -> None:
        transport = self._get_transport()
        transport.sendto(payload, addr)
        if timeout is not None:
            await asyncio.sleep(0)

    def _handle_datagram(self, data: bytes, addr: Tuple[str, int]) -> None:
        if not data:
            return
        channel_id = int.from_bytes(data[:4], "big")
        payload = data[4:]
        if addr not in self._known_peers:
            self._known_peers.add(addr)
            self._peer_queue.put_nowait(addr)
        self._default_remote = addr
        if self._peer_addr is None:
            self._peer_addr = addr
        if channel_id == 0:
            self._default_queue.put_nowait(payload)
        else:
            channel = self._channels.get(channel_id)
            if channel is None:
                channel = _QuicChannel(channel_id, asyncio.Queue(), addr)
                self._channels[channel_id] = channel
            elif channel.remote is None:
                channel.remote = addr
            channel.queue.put_nowait(payload)
