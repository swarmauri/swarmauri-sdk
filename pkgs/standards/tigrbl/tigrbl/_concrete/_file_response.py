"""Concrete file transport response."""

from __future__ import annotations

import mimetypes
from pathlib import Path

from ._response import Response


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


__all__ = ["FileResponse"]
