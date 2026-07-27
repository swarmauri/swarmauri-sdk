"""Transport-neutral bidirectional stream interfaces."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Iterator
from typing import Any, Mapping


class IBidirectionalStreamConnection(ABC):
    connection_id: str
    state: str

    @abstractmethod
    def send(self, event: Any) -> None: ...

    @abstractmethod
    async def asend(self, event: Any) -> None: ...

    @abstractmethod
    def receive(self) -> Any: ...

    @abstractmethod
    async def areceive(self) -> Any: ...

    @abstractmethod
    def iter_events(self) -> Iterator[Any]: ...

    @abstractmethod
    def aiter_events(self) -> AsyncIterator[Any]: ...

    @abstractmethod
    def close(self) -> None: ...

    @abstractmethod
    async def aclose(self) -> None: ...


class IBidirectionalStreamClient(ABC):
    @abstractmethod
    def connect(
        self,
        endpoint: str,
        *,
        headers: Mapping[str, str] | None = None,
        **kwargs: Any,
    ) -> IBidirectionalStreamConnection: ...

    @abstractmethod
    async def aconnect(
        self,
        endpoint: str,
        *,
        headers: Mapping[str, str] | None = None,
        **kwargs: Any,
    ) -> IBidirectionalStreamConnection: ...
