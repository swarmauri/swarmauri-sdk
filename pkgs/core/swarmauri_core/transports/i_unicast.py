"""Unicast transport interface."""

from __future__ import annotations

from abc import ABC, abstractmethod


class IUnicastTransport(ABC):
    """Interface for transports that support point-to-point messaging."""

    @abstractmethod
    async def send(
        self, target: str, data: bytes, *, timeout: float | None = None
    ) -> None:
        """Send data to a single target address."""

    @abstractmethod
    async def recv(self, *, timeout: float | None = None) -> bytes:
        """Receive data from the transport."""
