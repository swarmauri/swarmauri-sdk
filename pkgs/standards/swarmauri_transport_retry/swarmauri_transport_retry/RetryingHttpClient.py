"""HTTP client decorator that executes concrete retry policies."""

from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncIterator, Iterator, Mapping
from contextlib import asynccontextmanager, contextmanager
from typing import Any, Callable

from swarmauri_core.transports.http_errors import HttpRequestError
from swarmauri_core.transports.i_http_client import IHttpClient
from swarmauri_core.transports.i_http_response import IHttpResponse
from swarmauri_core.transports.i_http_retry_policy import IHttpRetryPolicy
from swarmauri_core.transports.i_http_stream_response import (
    IAsyncHttpStreamResponse,
    IHttpStreamResponse,
)
from swarmauri_core.transports.i_managed_http_client import IManagedHttpClient


class RetryingHttpClient(IManagedHttpClient):
    """Decorate any Swarmauri HTTP client with an explicit retry policy."""

    def __init__(
        self,
        *,
        client: IHttpClient,
        policy: IHttpRetryPolicy,
        sleep: Callable[[float], None] = time.sleep,
        async_sleep: Callable[[float], Any] = asyncio.sleep,
        own_client: bool = False,
    ) -> None:
        self.client = client
        self.policy = policy
        self._sleep = sleep
        self._async_sleep = async_sleep
        self.own_client = own_client

    def request(
        self,
        method: str,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        body: bytes = b"",
        **kwargs: Any,
    ) -> IHttpResponse:
        attempt = 1
        while True:
            try:
                response = self.client.request(
                    method,
                    path,
                    headers=headers,
                    body=body,
                    **kwargs,
                )
            except HttpRequestError as error:
                if not self.policy.should_retry(
                    method=method, attempt=attempt, error=error
                ):
                    raise
                self._sleep(self.policy.delay_seconds(attempt=attempt))
            else:
                if not self.policy.should_retry(
                    method=method, attempt=attempt, response=response
                ):
                    return response
                self._sleep(
                    self.policy.delay_seconds(
                        attempt=attempt, response=response
                    )
                )
            attempt += 1

    async def arequest(
        self,
        method: str,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        body: bytes = b"",
        **kwargs: Any,
    ) -> IHttpResponse:
        attempt = 1
        while True:
            try:
                response = await self.client.arequest(
                    method,
                    path,
                    headers=headers,
                    body=body,
                    **kwargs,
                )
            except HttpRequestError as error:
                if not self.policy.should_retry(
                    method=method, attempt=attempt, error=error
                ):
                    raise
                await self._async_sleep(
                    self.policy.delay_seconds(attempt=attempt)
                )
            else:
                if not self.policy.should_retry(
                    method=method, attempt=attempt, response=response
                ):
                    return response
                await self._async_sleep(
                    self.policy.delay_seconds(
                        attempt=attempt, response=response
                    )
                )
            attempt += 1

    @contextmanager
    def stream(
        self,
        method: str,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        body: bytes = b"",
        **kwargs: Any,
    ) -> Iterator[IHttpStreamResponse]:
        attempt = 1
        while True:
            try:
                with self.client.stream(
                    method,
                    path,
                    headers=headers,
                    body=body,
                    **kwargs,
                ) as response:
                    if not self.policy.should_retry(
                        method=method, attempt=attempt, response=response
                    ):
                        yield response
                        return
                    delay = self.policy.delay_seconds(
                        attempt=attempt, response=response
                    )
            except HttpRequestError as error:
                if not self.policy.should_retry(
                    method=method, attempt=attempt, error=error
                ):
                    raise
                delay = self.policy.delay_seconds(attempt=attempt)
            self._sleep(delay)
            attempt += 1

    @asynccontextmanager
    async def astream(
        self,
        method: str,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        body: bytes = b"",
        **kwargs: Any,
    ) -> AsyncIterator[IAsyncHttpStreamResponse]:
        attempt = 1
        while True:
            try:
                async with self.client.astream(
                    method,
                    path,
                    headers=headers,
                    body=body,
                    **kwargs,
                ) as response:
                    if not self.policy.should_retry(
                        method=method, attempt=attempt, response=response
                    ):
                        yield response
                        return
                    delay = self.policy.delay_seconds(
                        attempt=attempt, response=response
                    )
            except HttpRequestError as error:
                if not self.policy.should_retry(
                    method=method, attempt=attempt, error=error
                ):
                    raise
                delay = self.policy.delay_seconds(attempt=attempt)
            await self._async_sleep(delay)
            attempt += 1

    def close(self) -> None:
        if self.own_client and isinstance(self.client, IManagedHttpClient):
            self.client.close()

    async def aclose(self) -> None:
        if self.own_client and isinstance(self.client, IManagedHttpClient):
            await self.client.aclose()

    def __enter__(self) -> "RetryingHttpClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    async def __aenter__(self) -> "RetryingHttpClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.aclose()
