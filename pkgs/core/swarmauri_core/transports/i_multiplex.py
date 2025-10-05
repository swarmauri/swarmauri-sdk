"""Multiplex transport interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional, TypeAlias


ChannelHandle: TypeAlias = Any


class IMultiplexTransport(ABC):
    """Interface for transports that expose multiplexed channels."""

    @abstractmethod
    async def open_channel(self) -> ChannelHandle:
        """Open a logical channel on the transport."""

    @abstractmethod
    async def close_channel(self, handle: ChannelHandle) -> None:
        """Close a previously opened channel."""

    @abstractmethod
    async def send_on(
        self, handle: ChannelHandle, data: bytes, *, timeout: Optional[float] = None
    ) -> None:
        """Send data on a specific channel."""

    @abstractmethod
    async def recv_on(
        self, handle: ChannelHandle, *, timeout: Optional[float] = None
    ) -> bytes:
        """Receive data from a specific channel."""
