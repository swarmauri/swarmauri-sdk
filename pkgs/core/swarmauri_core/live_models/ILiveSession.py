"""Live-session interface."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Iterator
from .ILiveEvent import ILiveEvent
from .ILiveInput import ILiveInput


class ILiveSession(ABC):
    session_id: str
    state: str

    @abstractmethod
    def send(self, input_data: ILiveInput) -> None: ...

    @abstractmethod
    async def asend(self, input_data: ILiveInput) -> None: ...

    @abstractmethod
    def stream(self) -> Iterator[ILiveEvent]: ...

    @abstractmethod
    def astream(self) -> AsyncIterator[ILiveEvent]: ...

    @abstractmethod
    def close(self) -> None: ...

    @abstractmethod
    async def aclose(self) -> None: ...
