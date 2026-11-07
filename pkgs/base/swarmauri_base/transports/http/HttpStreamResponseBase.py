"""Synchronous streaming HTTP response base."""

from abc import abstractmethod
from collections.abc import Iterator

from swarmauri_core.transports.i_http_stream_response import (
    IHttpStreamResponse,
)

from .HttpResponseBase import HttpResponseBase


class HttpStreamResponseBase(HttpResponseBase, IHttpStreamResponse):
    @abstractmethod
    def iter_bytes(self) -> Iterator[bytes]: ...

    def iter_lines(self) -> Iterator[str]:
        pending = b""
        for chunk in self.iter_bytes():
            pending += chunk
            while b"\n" in pending:
                line, pending = pending.split(b"\n", 1)
                yield line.decode("utf-8", errors="replace")
        if pending:
            yield pending.decode("utf-8", errors="replace")
