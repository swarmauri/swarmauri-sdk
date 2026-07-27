"""Realtime agent interface."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Iterator
from typing import Any


class IRealtimeAgent(ABC):
    @abstractmethod
    def connect(self, **kwargs: Any) -> Any: ...

    @abstractmethod
    async def aconnect(self, **kwargs: Any) -> Any: ...

    @abstractmethod
    def send(self, input_data: Any) -> None: ...

    @abstractmethod
    async def asend(self, input_data: Any) -> None: ...

    @abstractmethod
    def stream(self) -> Iterator[Any]: ...

    @abstractmethod
    def astream(self) -> AsyncIterator[Any]: ...

    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> Any: ...

    @abstractmethod
    async def arun(self, *args: Any, **kwargs: Any) -> Any: ...

    @abstractmethod
    def interrupt(self) -> None: ...

    @abstractmethod
    async def ainterrupt(self) -> None: ...

    @abstractmethod
    def close(self) -> None: ...

    @abstractmethod
    async def aclose(self) -> None: ...
