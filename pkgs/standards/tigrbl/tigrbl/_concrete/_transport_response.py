"""Concrete transport response primitives and finalization helpers."""

from __future__ import annotations

import json as json_module
import mimetypes
from pathlib import Path
from typing import Any, AsyncIterator, Iterable

from ._response import Response

NO_BODY_STATUS = set(range(100, 200)) | {204, 205, 304}


class JSONResponse(Response):
    def __init__(self, content: Any, status_code: int = 200) -> None:
        payload = json_module.dumps(
            content, ensure_ascii=False, separators=(",", ":"), default=str
        ).encode("utf-8")
        super().__init__(
            status_code=status_code,
            headers=[("content-type", "application/json; charset=utf-8")],
            body=payload,
            media_type="application/json",
        )


class HTMLResponse(Response):
    def __init__(self, content: str, status_code: int = 200) -> None:
        super().__init__(
            status_code=status_code,
            headers=[("content-type", "text/html; charset=utf-8")],
            body=content.encode("utf-8"),
            media_type="text/html",
        )


class PlainTextResponse(Response):
    def __init__(self, content: str, status_code: int = 200) -> None:
        super().__init__(
            status_code=status_code,
            headers=[("content-type", "text/plain; charset=utf-8")],
            body=content.encode("utf-8"),
            media_type="text/plain",
        )


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


class FileResponse(Response):
    def __init__(self, path: str, media_type: str | None = None) -> None:
        payload = Path(path).read_bytes()
        content_type = (
            media_type or mimetypes.guess_type(path)[0] or "application/octet-stream"
        )
        super().__init__(
            status_code=200,
            headers=[("content-type", content_type)],
            body=payload,
            media_type=content_type,
        )
        self.path = str(path)


class RedirectResponse(Response):
    def __init__(self, url: str, status_code: int = 307) -> None:
        super().__init__(
            status_code=status_code,
            headers=[("location", url)],
            body=b"",
            media_type=None,
        )
        self.url = url


def finalize_transport_response(
    scope: dict[str, Any],
    status: int,
    headers: list[tuple[bytes, bytes]],
    body: bytes,
) -> tuple[list[tuple[bytes, bytes]], bytes]:
    """Enforce HTTP body/header invariants immediately before transport writes."""

    method = str(scope.get("method", "GET")).upper()

    if method == "HEAD" or status in NO_BODY_STATUS:
        drop = {b"content-length", b"content-type", b"transfer-encoding"}
        headers = [(k, v) for (k, v) in headers if k.lower() not in drop]
        return headers, b""

    headers = [(k, v) for (k, v) in headers if k.lower() != b"content-length"]
    headers.append((b"content-length", str(len(body)).encode("latin-1")))

    return headers, body


TransportResponse = Response

__all__ = [
    "TransportResponse",
    "Response",
    "JSONResponse",
    "HTMLResponse",
    "PlainTextResponse",
    "StreamingResponse",
    "FileResponse",
    "RedirectResponse",
    "NO_BODY_STATUS",
    "finalize_transport_response",
]
