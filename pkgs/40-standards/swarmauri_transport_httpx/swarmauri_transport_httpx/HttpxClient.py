from collections.abc import AsyncIterator, Iterator, Mapping
from contextlib import asynccontextmanager, contextmanager
from typing import Any

import httpx
from pydantic import Field, PrivateAttr
from swarmauri_base.transports.http.HttpClientBase import HttpClientBase
from swarmauri_core.transports.http_errors import HttpRequestError
from swarmauri_core.transports.i_managed_http_client import IManagedHttpClient

from .AsyncHttpxStreamResponse import AsyncHttpxStreamResponse
from .HttpxResponse import HttpxResponse
from .HttpxStreamResponse import HttpxStreamResponse


class HttpxClient(HttpClientBase, IManagedHttpClient):
    """Persistent HTTPX adapter for the Swarmauri HTTP client contracts."""

    client_options: dict[str, Any] = Field(default_factory=dict)
    _sync_client: httpx.Client | None = PrivateAttr(default=None)
    _async_client: httpx.AsyncClient | None = PrivateAttr(default=None)
    _owns_sync_client: bool = PrivateAttr(default=False)
    _owns_async_client: bool = PrivateAttr(default=False)

    def __init__(
        self,
        *,
        client: httpx.Client | None = None,
        async_client: httpx.AsyncClient | None = None,
        **data: Any,
    ) -> None:
        super().__init__(**data)
        self._sync_client = client
        self._async_client = async_client

    def _sync(self) -> httpx.Client:
        if self._sync_client is None:
            options = dict(self.client_options)
            options.setdefault("timeout", self.timeout)
            self._sync_client = httpx.Client(**options)
            self._owns_sync_client = True
        return self._sync_client

    def _async(self) -> httpx.AsyncClient:
        if self._async_client is None:
            options = dict(self.client_options)
            options.setdefault("timeout", self.timeout)
            self._async_client = httpx.AsyncClient(**options)
            self._owns_async_client = True
        return self._async_client

    @staticmethod
    def _request_kwargs(body: bytes, kwargs: dict[str, Any]) -> dict[str, Any]:
        request_kwargs = dict(kwargs)
        if body:
            if any(
                key in request_kwargs
                for key in ("content", "data", "files", "json")
            ):
                raise ValueError(
                    "body cannot be combined with content, data, files, "
                    "or json"
                )
            request_kwargs["content"] = body
        return request_kwargs

    def request(
        self,
        method: str,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        body: bytes = b"",
        **kwargs: Any,
    ) -> HttpxResponse:
        try:
            response = self._sync().request(
                method,
                self.resolve_url(path),
                headers=self.merge_headers(dict(headers or {})),
                **self._request_kwargs(body, kwargs),
            )
            return HttpxResponse.from_response(response)
        except httpx.RequestError as error:
            raise HttpRequestError(str(error)) from error

    async def arequest(
        self,
        method: str,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        body: bytes = b"",
        **kwargs: Any,
    ) -> HttpxResponse:
        try:
            response = await self._async().request(
                method,
                self.resolve_url(path),
                headers=self.merge_headers(dict(headers or {})),
                **self._request_kwargs(body, kwargs),
            )
            return HttpxResponse.from_response(response)
        except httpx.RequestError as error:
            raise HttpRequestError(str(error)) from error

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
        try:
            with self._sync().stream(
                method,
                self.resolve_url(path),
                headers=self.merge_headers(dict(headers or {})),
                **self._request_kwargs(body, kwargs),
            ) as response:
                yield HttpxStreamResponse.from_response(response)
        except httpx.RequestError as error:
            raise HttpRequestError(str(error)) from error

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
        try:
            async with self._async().stream(
                method,
                self.resolve_url(path),
                headers=self.merge_headers(dict(headers or {})),
                **self._request_kwargs(body, kwargs),
            ) as response:
                yield AsyncHttpxStreamResponse.from_response(response)
        except httpx.RequestError as error:
            raise HttpRequestError(str(error)) from error

    def close(self) -> None:
        if self._sync_client is not None and self._owns_sync_client:
            self._sync_client.close()
        self._sync_client = None
        self._owns_sync_client = False

    async def aclose(self) -> None:
        if self._async_client is not None and self._owns_async_client:
            await self._async_client.aclose()
        self._async_client = None
        self._owns_async_client = False

    def __enter__(self) -> "HttpxClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    async def __aenter__(self) -> "HttpxClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.aclose()
