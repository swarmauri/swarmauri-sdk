"""HTTP utilities for resilient Apple identity provider requests."""

from __future__ import annotations

import asyncio
import random
from typing import Final

import httpx


class RetryingAsyncClient(httpx.AsyncClient):
    """Async HTTP client implementing exponential backoff retries."""

    _DEFAULT_TIMEOUT: Final[float] = 30.0

    def __init__(self, *, timeout_sec: float | None = None, **kwargs) -> None:
        timeout = httpx.Timeout(timeout_sec or self._DEFAULT_TIMEOUT)
        super().__init__(timeout=timeout, **kwargs)

    async def _sleep(
        self, attempt: int, *, base: float = 0.25, cap: float = 4.0
    ) -> None:
        """Sleep using exponential backoff with jitter."""

        delay = min(cap, base * (2**attempt)) * (1.0 + 0.1 * random.random())
        await asyncio.sleep(delay)

    async def post_retry(
        self, url: str, *, max_retries: int = 4, **kwargs
    ) -> httpx.Response:
        """POST with retry semantics for transient failures."""

        for attempt in range(max_retries + 1):
            response = await self.post(url, **kwargs)
            if response.status_code < 500 and response.status_code not in (429,):
                return response
            await self._sleep(attempt)
        response.raise_for_status()
        return response

    async def get_retry(
        self, url: str, *, max_retries: int = 4, **kwargs
    ) -> httpx.Response:
        """GET with retry semantics for transient failures."""

        for attempt in range(max_retries + 1):
            response = await self.get(url, **kwargs)
            if response.status_code < 500 and response.status_code not in (429,):
                return response
            await self._sleep(attempt)
        response.raise_for_status()
        return response
