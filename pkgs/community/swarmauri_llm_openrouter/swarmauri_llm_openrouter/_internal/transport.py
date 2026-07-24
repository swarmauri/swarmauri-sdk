"""Provide shared HTTP transport for OpenRouter model families."""

import json
from collections.abc import AsyncIterator, Iterator
from typing import Any

import httpx


class OpenRouterTransport:
    """Send synchronous and asynchronous OpenRouter API requests."""

    def __init__(self, base_url: str, headers: dict[str, str], timeout: float):
        self.base_url = base_url.rstrip("/")
        self.headers = headers
        self.timeout = timeout

    def request(
        self,
        method: str,
        path: str,
        *,
        json_data: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Send an HTTP request and raise for an unsuccessful response."""
        url = (
            path
            if path.startswith(("http://", "https://"))
            else (f"{self.base_url}/{path.lstrip('/')}")
        )
        response = httpx.request(
            method,
            url,
            headers=self.headers,
            json=json_data,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response

    async def arequest(
        self,
        method: str,
        path: str,
        *,
        json_data: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Send an asynchronous request and raise for failure."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method,
                f"{self.base_url}/{path.lstrip('/')}",
                headers=self.headers,
                json=json_data,
            )
        response.raise_for_status()
        return response

    def stream(self, path: str, payload: dict[str, Any]) -> Iterator[dict]:
        """Yield decoded server-sent event payloads."""
        with httpx.stream(
            "POST",
            f"{self.base_url}/{path.lstrip('/')}",
            headers=self.headers,
            json=payload,
            timeout=self.timeout,
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                event = self._decode_sse_line(line)
                if event is not None:
                    yield event

    async def astream(
        self, path: str, payload: dict[str, Any]
    ) -> AsyncIterator[dict]:
        """Yield asynchronously decoded server-sent event payloads."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/{path.lstrip('/')}",
                headers=self.headers,
                json=payload,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    event = self._decode_sse_line(line)
                    if event is not None:
                        yield event

    @staticmethod
    def _decode_sse_line(line: str) -> dict[str, Any] | None:
        """Decode one OpenRouter SSE data line."""
        if not line or line.startswith(":") or not line.startswith("data:"):
            return None
        data = line[5:].strip()
        if not data or data == "[DONE]":
            return None
        return json.loads(data)
