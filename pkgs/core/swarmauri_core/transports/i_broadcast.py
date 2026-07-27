"""Broadcast transport interface."""

from __future__ import annotations

from abc import ABC, abstractmethod


class IBroadcastTransport(ABC):
    """Interface for transports supporting broadcast messages."""

    @abstractmethod
    async def broadcast(
        self, data: bytes, *, timeout: float | None = None
    ) -> None:
        """Broadcast data to all peers reachable by the transport."""
