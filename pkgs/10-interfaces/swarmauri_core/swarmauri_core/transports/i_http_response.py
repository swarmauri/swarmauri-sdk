"""HTTP response interface."""

from abc import ABC, abstractmethod
from typing import Any, Mapping


class IHttpResponse(ABC):
    status_code: int
    headers: Mapping[str, str]

    @abstractmethod
    def read(self) -> bytes: ...

    @abstractmethod
    async def aread(self) -> bytes: ...

    @abstractmethod
    def json(self) -> Any: ...

    @abstractmethod
    def raise_for_status(self) -> None:
        """Raise ``HttpStatusError`` for an unsuccessful response."""
        ...
