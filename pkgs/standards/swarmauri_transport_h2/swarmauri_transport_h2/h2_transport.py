from __future__ import annotations

import asyncio
from typing import Dict, List, Optional, Tuple

from swarmauri_base.transports.http_client_mixin import HttpClientMixin
from swarmauri_base.transports.http_server_mixin import HttpServerMixin
from swarmauri_base.transports.runnable_mixin import RunnableMixin
from swarmauri_base.transports.transport_base import TransportBase
from swarmauri_core.transports.capabilities import TransportCapabilities
from swarmauri_core.transports.enums import Feature

from swarmauri_transport_h2mux import H2MuxTransport
from swarmauri_base.transports.multiplex_mixin import ChannelHandle

Bytes = bytes
Headers = Dict[str, str]


class H2Transport(TransportBase, RunnableMixin, HttpServerMixin, HttpClientMixin):
    """HTTP/2 transport adapter that layers HTTP semantics on top of ``H2MuxTransport``."""

    def __init__(self, allow_h2c: bool = False):
        super().__init__(name="H2Transport")
        self._mux = H2MuxTransport(allow_h2c=allow_h2c)

    def supports(self) -> TransportCapabilities:
        caps = self._mux.supports()
        return TransportCapabilities(
            protocols=caps.protocols,
            io=caps.io,
            casts=caps.casts,
            features=frozenset(set(caps.features) | {Feature.MULTIPLEX}),
            security=caps.security,
            schemes=caps.schemes,
        )

    async def _start_server(self, **kwargs) -> None:
        await self._mux._start_server(**kwargs)

    async def _stop_server(self) -> None:
        await self._mux._stop_server()

    async def _open_client(self, **kwargs) -> None:
        await self._mux._open_client(**kwargs)

    async def _close_client(self) -> None:
        await self._mux._close_client()

    async def serve_stream(
        self, stream_id: int, req_headers: Headers, body: Bytes
    ) -> None:
        application = self.app
        status, response_headers, response_body = await application(
            req_headers.get(":method", "GET"),
            req_headers.get(":path", "/"),
            {k: v for k, v in req_headers.items() if not k.startswith(":")},
            body,
        )
        header_block = [(":status", str(status))]
        header_block.extend((k.lower(), v) for k, v in response_headers.items())
        self._mux._h2.send_headers(
            stream_id, header_block, end_stream=not response_body
        )  # type: ignore[attr-defined]
        if response_body:
            self._mux._h2.send_data(stream_id, response_body, end_stream=True)
        await self._mux._flush()

    async def request(
        self,
        method: str,
        path: str,
        headers: Headers | None = None,
        body: Bytes = b"",
        channel: ChannelHandle | None = None,
    ) -> Tuple[int, Headers, Bytes]:
        owned = False
        if channel is None:
            channel = await self._mux.open_channel()
            owned = True

        header_block = [
            (":method", method),
            (":path", path),
            (":scheme", "https"),
            (":authority", "localhost"),
        ]
        for key, value in (headers or {}).items():
            header_block.append((key.lower(), value))
        self._mux._h2.send_headers(channel, header_block, end_stream=not body)
        if body:
            self._mux._h2.send_data(channel, body, end_stream=True)
        await self._mux._flush()

        status: Optional[int] = None
        response_headers: Headers = {}
        payload: List[bytes] = []

        while True:
            if self._mux._reader is None:
                await asyncio.sleep(0)
                continue
            data = await self._mux._reader.read(65536)
            if not data:
                break
            for event in self._mux._h2.receive_data(data):
                from h2.events import (
                    DataReceived,
                    ResponseReceived,
                    StreamEnded,
                    StreamReset,
                )

                if isinstance(event, ResponseReceived) and event.stream_id == channel:
                    for key, value in event.headers:
                        if key == b":status":
                            status = int(value.decode())
                        elif not key.startswith(b":"):
                            response_headers[key.decode().lower()] = value.decode()
                elif isinstance(event, DataReceived) and event.stream_id == channel:
                    payload.append(event.data)
                    self._mux._h2.acknowledge_received_data(
                        len(event.data), event.stream_id
                    )
                elif isinstance(event, StreamEnded) and event.stream_id == channel:
                    await self._mux._flush()
                    if owned:
                        await self._mux.close_channel(channel)
                    return status or 200, response_headers, b"".join(payload)
                elif isinstance(event, StreamReset) and event.stream_id == channel:
                    if owned:
                        await self._mux.close_channel(channel)
                    raise RuntimeError("HTTP/2 stream reset")
            await self._mux._flush()

        if owned:
            await self._mux.close_channel(channel)
        return status or 500, response_headers, b"".join(payload)
