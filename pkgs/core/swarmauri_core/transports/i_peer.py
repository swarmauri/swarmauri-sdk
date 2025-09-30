"""Peer transport interface for accepting connections."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncIterator, Any


class IPeerTransport(ABC):
    """Interface for transports that accept inbound peers."""

    @abstractmethod
    async def accept(self) -> AsyncIterator[Any]:  # type: ignore[override]
        """Return an asynchronous iterator of newly connected peers."""
