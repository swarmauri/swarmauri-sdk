from __future__ import annotations

import asyncio
import contextlib
import ssl
from collections import deque
from typing import Deque, Dict, Optional, Tuple

from swarmauri_base.transports.multiplex_mixin import (
    ChannelHandle,
    MultiplexTransportMixin,
)
from swarmauri_base.transports.peer_mixin import PeerTransportMixin
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


class H2MuxTransport(
    TransportBase, RunnableMixin, PeerTransportMixin, MultiplexTransportMixin
):
    """HTTP/2 multiplexed connection without HTTP application semantics."""

    def __init__(self, allow_h2c: bool = False):
        super().__init__(name="H2Mux")
        self._allow_h2c = allow_h2c
        self._srv: asyncio.AbstractServer | None = None
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._h2 = None
        self._streams: Dict[int, Deque[bytes]] = {}
        self._next_sid = 1
        self._recv_wait: Tuple[int, asyncio.Future[bytes]] | None = None

    def supports(self) -> TransportCapabilities:
        schemes = {AddressScheme.HTTPS}
        if self._allow_h2c:
            schemes.add(AddressScheme.H2C)
        return TransportCapabilities(
            protocols=frozenset({Protocol.H2}),
            io=IOModel.STREAM,
            casts=frozenset({Cast.UNICAST}),
            features=frozenset({Feature.RELIABLE, Feature.ORDERED, Feature.MULTIPLEX}),
            security=SecurityMode.TLS,
            schemes=frozenset(schemes),
        )

    async def _start_server(
        self,
        host: str = "0.0.0.0",
        port: int = 8443,
        ssl_ctx: Optional[ssl.SSLContext] = None,
    ) -> None:
        if ssl_ctx:
            with contextlib.suppress(Exception):
                ssl_ctx.set_alpn_protocols(["h2"])

        async def _handler(
            reader: asyncio.StreamReader, writer: asyncio.StreamWriter
        ) -> None:
            await self._serve_conn(reader, writer, is_server=True)

        self._srv = await asyncio.start_server(_handler, host, port, ssl=ssl_ctx)

    async def _stop_server(self) -> None:
        if self._srv is not None:
            self._srv.close()
            await self._srv.wait_closed()
            self._srv = None

    async def _open_client(
        self,
        host: str = "127.0.0.1",
        port: int = 8443,
        server_hostname: Optional[str] = None,
        ssl_ctx: Optional[ssl.SSLContext] = None,
    ) -> None:
        if ssl_ctx:
            with contextlib.suppress(Exception):
                ssl_ctx.set_alpn_protocols(["h2"])
        self._reader, self._writer = await asyncio.open_connection(
            host,
            port,
            ssl=ssl_ctx,
            server_hostname=server_hostname,
        )
        await self._init_h2(is_server=False)

    async def _close_client(self) -> None:
        await self._close_h2()
        if self._writer is not None:
            self._writer.close()
            with contextlib.suppress(Exception):
                await self._writer.wait_closed()
        self._reader = None
        self._writer = None

    async def open_channel(self) -> ChannelHandle:  # type: ignore[override]
        if self._h2 is None:
            raise RuntimeError("H2 not initialized")
        stream_id = self._next_sid
        self._next_sid += 2
        self._streams[stream_id] = deque()
        return stream_id

    async def close_channel(self, handle: ChannelHandle) -> None:  # type: ignore[override]
        if self._h2 is not None:
            with contextlib.suppress(Exception):
                self._h2.end_stream(handle)
            await self._flush()
        self._streams.pop(handle, None)

    async def send_on(
        self,
        handle: ChannelHandle,
        data: bytes,
        *,
        timeout: Optional[float] = None,
    ) -> None:  # type: ignore[override]
        if self._h2 is None or self._writer is None:
            raise RuntimeError("not connected")
        self._h2.send_data(handle, data)
        await asyncio.wait_for(self._flush(), timeout=timeout)

    async def recv_on(
        self,
        handle: ChannelHandle,
        *,
        timeout: Optional[float] = None,
    ) -> bytes:  # type: ignore[override]
        queue = self._streams.get(handle)
        if queue and queue:
            return queue.popleft()
        loop = asyncio.get_running_loop()
        future: asyncio.Future[bytes] = loop.create_future()
        self._recv_wait = (handle, future)
        return await asyncio.wait_for(future, timeout=timeout)

    async def _serve_conn(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        *,
        is_server: bool,
    ) -> None:
        self._reader = reader
        self._writer = writer
        await self._init_h2(is_server=is_server)
        try:
            while True:
                data = await reader.read(65536)
                if not data:
                    break
                for event in self._h2.receive_data(data):
                    from h2.events import DataReceived, StreamEnded

                    if isinstance(event, DataReceived):
                        deque_ = self._streams.setdefault(event.stream_id, deque())
                        deque_.append(event.data)
                        self._h2.acknowledge_received_data(
                            len(event.data), event.stream_id
                        )
                        if self._recv_wait and self._recv_wait[0] == event.stream_id:
                            _, fut = self._recv_wait
                            if not fut.done():
                                fut.set_result(deque_.popleft())
                    elif isinstance(event, StreamEnded):
                        self._streams.setdefault(event.stream_id, deque())
                await self._flush()
        finally:
            await self._close_h2()
            writer.close()
            with contextlib.suppress(Exception):
                await writer.wait_closed()

    async def _init_h2(self, *, is_server: bool) -> None:
        try:
            from h2.config import H2Configuration
            from h2.connection import H2Connection
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("Install 'h2' package for H2MuxTransport") from exc

        config = H2Configuration(client=not is_server, header_encoding="utf-8")
        self._h2 = H2Connection(config)
        self._h2.initiate_connection()
        await self._flush()

    async def _close_h2(self) -> None:
        if self._h2 is None:
            return
        with contextlib.suppress(Exception):
            self._h2.close_connection()
            await self._flush()
        self._h2 = None
        self._streams.clear()
        self._recv_wait = None

    async def _flush(self) -> None:
        if self._writer is None or self._h2 is None:
            return
        data = self._h2.data_to_send()
        if data:
            self._writer.write(data)
            await self._writer.drain()
