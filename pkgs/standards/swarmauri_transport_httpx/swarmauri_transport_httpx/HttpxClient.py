from collections.abc import AsyncIterator, Iterator, Mapping
from contextlib import asynccontextmanager, contextmanager
from typing import Any

import httpx
from swarmauri_base.transports.http.HttpClientBase import HttpClientBase

from .AsyncHttpxStreamResponse import AsyncHttpxStreamResponse
from .HttpxResponse import HttpxResponse
from .HttpxStreamResponse import HttpxStreamResponse


class HttpxClient(HttpClientBase):
    def request(
        self,
        method: str,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        body: bytes = b"",
        **kwargs: Any,
    ) -> HttpxResponse:
        with httpx.Client(timeout=self.timeout) as client:
            response = client.request(
                method,
                self.resolve_url(path),
                headers=self.merge_headers(dict(headers or {})),
                content=body,
                **kwargs,
            )
            return HttpxResponse.from_response(response)

    async def arequest(
        self,
        method: str,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        body: bytes = b"",
        **kwargs: Any,
    ) -> HttpxResponse:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method,
                self.resolve_url(path),
                headers=self.merge_headers(dict(headers or {})),
                content=body,
                **kwargs,
            )
            return HttpxResponse.from_response(response)

    @contextmanager
    def stream(
        self,
        method: str,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        body: bytes = b"",
        **kwargs: Any,
    ) -> Iterator[HttpxStreamResponse]:
        with httpx.Client(timeout=self.timeout) as client:
            with client.stream(
                method,
                self.resolve_url(path),
                headers=self.merge_headers(dict(headers or {})),
                content=body,
                **kwargs,
            ) as response:
                yield HttpxStreamResponse.from_response(response)

    @asynccontextmanager
    async def astream(
        self,
        method: str,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        body: bytes = b"",
        **kwargs: Any,
    ) -> AsyncIterator[AsyncHttpxStreamResponse]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                method,
                self.resolve_url(path),
                headers=self.merge_headers(dict(headers or {})),
                content=body,
                **kwargs,
            ) as response:
                yield AsyncHttpxStreamResponse.from_response(response)
