from __future__ import annotations

import asyncio
from typing import Awaitable, Callable, Optional

from swarmauri_base.transports.http_server_mixin import HttpServerMixin
from swarmauri_base.transports.runnable_mixin import RunnableMixin
from swarmauri_base.transports.transport_base import TransportBase
from swarmauri_core.transports.capabilities import TransportCapabilities
from swarmauri_core.transports.enums import (
    AddressScheme,
    Cast,
    Feature,
    IOModel,
    Protocol,
    SecurityMode,
)

ASGIApp = Callable[..., Awaitable[None]]


class ASGITransport(TransportBase, RunnableMixin, HttpServerMixin):
    """In-process ASGI server transport using Uvicorn."""

    def __init__(self, app: Optional[ASGIApp] = None) -> None:
        super().__init__(name="ASGI")
        if app is not None:
            self.set_app(app)
        self._server = None

    def supports(self) -> TransportCapabilities:
        return TransportCapabilities(
            protocols=frozenset({Protocol.HTTP1, Protocol.H2}),
            io=IOModel.STREAM,
            casts=frozenset({Cast.UNICAST}),
            features=frozenset({Feature.RELIABLE, Feature.ORDERED, Feature.MULTIPLEX}),
            security=SecurityMode.TLS,
            schemes=frozenset({AddressScheme.HTTP, AddressScheme.HTTPS}),
        )

    async def _start_server(
        self,
        host: str = "0.0.0.0",
        port: int = 8000,
        ssl_ctx=None,
        workers: int = 1,
    ) -> None:
        if self._app is None:
            raise RuntimeError("ASGI app not set")
        try:
            import uvicorn
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("Install 'uvicorn' for ASGITransport") from exc

        config = uvicorn.Config(
            self._app,
            host=host,
            port=port,
            ssl=ssl_ctx,
            loop="asyncio",
            workers=workers,
        )
        self._server = uvicorn.Server(config)
        asyncio.create_task(self._server.serve())

    async def _stop_server(self) -> None:
        if self._server is not None:
            self._server.should_exit = True
            self._server = None

    async def _open_client(self, **kwargs) -> None:
        raise NotImplementedError("ASGI transport does not act as a client")

    async def _close_client(self) -> None:
        return None
