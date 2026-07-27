"""Multiplex transport interface."""

from abc import ABC, abstractmethod
from typing import Any, Optional, TypeAlias

ChannelHandle: TypeAlias = Any


class IMultiplexTransport(ABC):
    @abstractmethod
    def open_channel(self) -> ChannelHandle: ...

    @abstractmethod
    async def aopen_channel(self) -> ChannelHandle: ...

    @abstractmethod
    def close_channel(self, handle: ChannelHandle) -> None: ...

    @abstractmethod
    async def aclose_channel(self, handle: ChannelHandle) -> None: ...

    @abstractmethod
    def send_on(
        self,
        handle: ChannelHandle,
        data: bytes,
        *,
        timeout: Optional[float] = None,
    ) -> None: ...

    @abstractmethod
    async def asend_on(
        self,
        handle: ChannelHandle,
        data: bytes,
        *,
        timeout: Optional[float] = None,
    ) -> None: ...

    @abstractmethod
    def receive_on(
        self, handle: ChannelHandle, *, timeout: Optional[float] = None
    ) -> bytes: ...

    @abstractmethod
    async def areceive_on(
        self, handle: ChannelHandle, *, timeout: Optional[float] = None
    ) -> bytes: ...
