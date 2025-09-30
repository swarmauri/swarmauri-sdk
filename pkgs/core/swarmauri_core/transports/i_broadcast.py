"""Broadcast transport interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class IBroadcastTransport(ABC):
    """Interface for transports supporting broadcast messages."""

    @abstractmethod
    async def broadcast(self, data: bytes, *, timeout: Optional[float] = None) -> None:
        """Broadcast data to all peers reachable by the transport."""
