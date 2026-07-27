"""Unified synchronous and asynchronous HTTP client interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from typing import Any, Mapping, Optional

from .i_http_response import IHttpResponse
from .i_http_stream_response import (
    IAsyncHttpStreamResponse,
    IHttpStreamResponse,
)

Headers = Mapping[str, str]


class IHttpClient(ABC):
    """Contract for buffered and streaming HTTP requests."""

    @abstractmethod
    def request(
        self,
        method: str,
        path: str,
        *,
        headers: Optional[Headers] = None,
        body: bytes = b"",
        **kwargs: Any,
    ) -> IHttpResponse: ...

    @abstractmethod
    async def arequest(
        self,
        method: str,
        path: str,
        *,
        headers: Optional[Headers] = None,
        body: bytes = b"",
        **kwargs: Any,
    ) -> IHttpResponse: ...

    @abstractmethod
    def stream(
        self,
        method: str,
        path: str,
        *,
        headers: Optional[Headers] = None,
        body: bytes = b"",
        **kwargs: Any,
    ) -> AbstractContextManager[IHttpStreamResponse]: ...

    @abstractmethod
    def astream(
        self,
        method: str,
        path: str,
        *,
        headers: Optional[Headers] = None,
        body: bytes = b"",
        **kwargs: Any,
    ) -> AbstractAsyncContextManager[IAsyncHttpStreamResponse]: ...
