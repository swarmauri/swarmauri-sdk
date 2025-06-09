from __future__ import annotations

import abc
from typing import Any, Generic, TypeVar

SendT = TypeVar("SendT", contravariant=True)
RecvT = TypeVar("RecvT", covariant=True)


class ITransport(abc.ABC, Generic[SendT, RecvT]):
    """Universal async transport contract (stateless or stateful)."""

    @abc.abstractmethod
    async def connect(self, **opts: Any) -> None:
        """Establish the underlying connection (noop for stateless transports)."""

    @abc.abstractmethod
    async def close(self) -> None:
        """Tear down the connection and release resources."""

    @abc.abstractmethod
    def is_connected(self) -> bool:
        """Return ``True`` while an active connection exists."""

    @abc.abstractmethod
    async def send(self, msg: SendT, **meta: Any) -> None:
        """Send a single message (and optional metadata)."""

    @abc.abstractmethod
    async def recv(self, **opts: Any) -> RecvT:
        """Receive a single message (blocking until something is available)."""

    async def __aenter__(self) -> "ITransport[SendT, RecvT]":
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> bool:
        await self.close()
        return False
