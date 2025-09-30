"""Multicast transport interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Sequence


class IMulticastTransport(ABC):
    """Interface for transports capable of multicast delivery."""

    @abstractmethod
    async def multicast(
        self, group: Sequence[str], data: bytes, *, timeout: Optional[float] = None
    ) -> None:
        """Send data to a multicast group."""
