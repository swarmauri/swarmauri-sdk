"""Concrete streaming transport response."""

from __future__ import annotations

from typing import AsyncIterator, Iterable

from ._response import Response


class StreamingResponse(Response):
    def __init__(
        self,
        content: Iterable[bytes] | bytes,
        status_code: int = 200,
        media_type: str = "application/octet-stream",
    ) -> None:
        chunks = [content] if isinstance(content, bytes) else list(content)
        super().__init__(
            status_code=status_code,
            headers=[("content-type", media_type)],
            body=b"".join(chunks),
            media_type=media_type,
        )
        self._chunks = [bytes(chunk) for chunk in chunks]

    @property
    def body_iterator(self) -> AsyncIterator[bytes]:
        async def _iter() -> AsyncIterator[bytes]:
            for chunk in self._chunks:
                yield chunk

        return _iter()


__all__ = ["StreamingResponse"]
