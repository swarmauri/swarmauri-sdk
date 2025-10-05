"""Base transport interface shared across all concrete transports."""

from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager
from typing import Any

from .capabilities import TransportCapabilities


class ITransport(ABC):
    """Capability-aware transport interface."""

    @abstractmethod
    def supports(self) -> TransportCapabilities:
        """Return the capability set advertised by the transport."""

    @abstractmethod
    def server(self, **bind_kwargs: Any) -> AbstractAsyncContextManager["ITransport"]:
        """Return a context manager that starts the transport's server side."""

    @abstractmethod
    def client(
        self, **connect_kwargs: Any
    ) -> AbstractAsyncContextManager["ITransport"]:
        """Return a context manager that opens the transport's client side."""

    @abstractmethod
    async def _start_server(self, **bind_kwargs: Any) -> None:
        """Hook invoked when the server context is entered."""

    @abstractmethod
    async def _stop_server(self) -> None:
        """Hook invoked when the server context exits."""

    @abstractmethod
    async def _open_client(self, **connect_kwargs: Any) -> None:
        """Hook invoked when the client context is entered."""

    @abstractmethod
    async def _close_client(self) -> None:
        """Hook invoked when the client context exits."""
