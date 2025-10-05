from __future__ import annotations

import asyncio
import contextlib
from typing import Optional

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


class MeshSidecarHttp2(TransportBase, RunnableMixin, PeerTransportMixin):
    """Client transport that communicates with a local service-mesh sidecar."""

    def __init__(self) -> None:
        super().__init__(name="MeshSidecarH2")
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None

    def supports(self) -> TransportCapabilities:
        return TransportCapabilities(
            protocols=frozenset({Protocol.H2}),
            io=IOModel.STREAM,
            casts=frozenset({Cast.UNICAST}),
            features=frozenset(
                {
                    Feature.RELIABLE,
                    Feature.ORDERED,
                    Feature.MULTIPLEX,
                    Feature.TERMINATED_AT_SIDECAR,
                }
            ),
            security=SecurityMode.MESH_MTLS,
            schemes=frozenset({AddressScheme.HTTPS}),
        )

    async def _start_server(self, **kwargs) -> None:
        raise NotImplementedError("Server role is handled by the service mesh sidecar")

    async def _stop_server(self) -> None:
        return None

    async def _open_client(
        self,
        uds_path: Optional[str] = None,
        host: str = "127.0.0.1",
        port: int = 15001,
    ) -> None:
        if uds_path:
            self._reader, self._writer = await asyncio.open_unix_connection(uds_path)
        else:
            self._reader, self._writer = await asyncio.open_connection(host, port)

    async def _close_client(self) -> None:
        if self._writer is not None:
            self._writer.close()
            with contextlib.suppress(Exception):
                await self._writer.wait_closed()
        self._reader = None
        self._writer = None
