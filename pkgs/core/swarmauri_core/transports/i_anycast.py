"""Anycast transport interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Sequence


class IAnycastTransport(ABC):
    """Interface for transports that can deliver to any of multiple candidates."""

    @abstractmethod
    async def anycast(
        self, candidates: Sequence[str], data: bytes, *, timeout: Optional[float] = None
    ) -> str:
        """Send data to one of the candidate addresses and return the chosen target."""
