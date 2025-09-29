"""Unicast transport interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class IUnicastTransport(ABC):
    """Interface for transports that support point-to-point messaging."""

    @abstractmethod
    async def send(
        self, target: str, data: bytes, *, timeout: Optional[float] = None
    ) -> None:
        """Send data to a single target address."""

    @abstractmethod
    async def recv(self, *, timeout: Optional[float] = None) -> bytes:
        """Receive data from the transport."""
