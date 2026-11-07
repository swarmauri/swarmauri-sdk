"""Asynchronous streaming HTTP response base."""

from abc import abstractmethod
from collections.abc import AsyncIterator

from swarmauri_core.transports.i_http_stream_response import (
    IAsyncHttpStreamResponse,
)

from .HttpResponseBase import HttpResponseBase


class AsyncHttpStreamResponseBase(HttpResponseBase, IAsyncHttpStreamResponse):
    @abstractmethod
    def aiter_bytes(self) -> AsyncIterator[bytes]: ...

    async def aiter_lines(self) -> AsyncIterator[str]:
        pending = b""
        async for chunk in self.aiter_bytes():
            pending += chunk
            while b"\n" in pending:
                line, pending = pending.split(b"\n", 1)
                yield line.decode("utf-8", errors="replace")
        if pending:
            yield pending.decode("utf-8", errors="replace")
