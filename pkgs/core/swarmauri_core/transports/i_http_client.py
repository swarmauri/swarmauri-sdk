"""Unified synchronous and asynchronous HTTP client interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from typing import Any, Mapping

from .i_http_response import IHttpResponse
from .i_http_stream_response import (
    IAsyncHttpStreamResponse,
    IHttpStreamResponse,
)

Headers = Mapping[str, str]


class IHttpClient(ABC):
    """Contract for buffered and streaming HTTP requests.

    ``path`` may be either an absolute HTTP URL or a path relative to an
    implementation-defined base URL. Concrete keyword arguments such as
    ``json``, ``data``, ``files``, and ``params`` are intentionally passed
    through so adapters can expose the capabilities of their HTTP stack.
    """

    @abstractmethod
    def request(
        self,
        method: str,
        path: str,
        *,
        headers: Headers | None = None,
        body: bytes = b"",
        **kwargs: Any,
    ) -> IHttpResponse: ...

    @abstractmethod
    async def arequest(
        self,
        method: str,
        path: str,
        *,
        headers: Headers | None = None,
        body: bytes = b"",
        **kwargs: Any,
    ) -> IHttpResponse: ...

    @abstractmethod
    def stream(
        self,
        method: str,
        path: str,
        *,
        headers: Headers | None = None,
        body: bytes = b"",
        **kwargs: Any,
    ) -> AbstractContextManager[IHttpStreamResponse]: ...

    @abstractmethod
    def astream(
        self,
        method: str,
        path: str,
        *,
        headers: Headers | None = None,
        body: bytes = b"",
        **kwargs: Any,
    ) -> AbstractAsyncContextManager[IAsyncHttpStreamResponse]: ...
