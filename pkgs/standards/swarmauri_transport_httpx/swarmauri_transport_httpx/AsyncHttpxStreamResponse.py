from collections.abc import AsyncIterator
from typing import Any

from pydantic import PrivateAttr
from swarmauri_base.transports.http.AsyncHttpStreamResponseBase import (
    AsyncHttpStreamResponseBase,
)


class AsyncHttpxStreamResponse(AsyncHttpStreamResponseBase):
    _response: Any = PrivateAttr(default=None)

    @classmethod
    def from_response(cls, response: Any) -> "AsyncHttpxStreamResponse":
        result = cls(
            status_code=response.status_code,
            headers=dict(response.headers),
        )
        result._response = response
        return result

    async def aiter_bytes(self) -> AsyncIterator[bytes]:
        async for chunk in self._response.aiter_bytes():
            yield chunk

    async def aread(self) -> bytes:
        return await self._response.aread()

    def json(self) -> Any:
        return self._response.json()

    def raise_for_status(self) -> None:
        self._response.raise_for_status()
