"""Streaming HTTP response interfaces."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Iterator

from .i_http_response import IHttpResponse


class IHttpStreamResponse(IHttpResponse, ABC):
    @abstractmethod
    def iter_bytes(self) -> Iterator[bytes]: ...

    @abstractmethod
    def iter_lines(self) -> Iterator[str]: ...


class IAsyncHttpStreamResponse(IHttpResponse, ABC):
    @abstractmethod
    def aiter_bytes(self) -> AsyncIterator[bytes]: ...

    @abstractmethod
    def aiter_lines(self) -> AsyncIterator[str]: ...
