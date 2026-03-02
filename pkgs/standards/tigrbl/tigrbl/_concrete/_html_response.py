"""Concrete HTML response primitive."""

from __future__ import annotations

from ._response import Response


class HTMLResponse(Response):
    def __init__(self, content: str, status_code: int = 200) -> None:
        super().__init__(
            status_code=status_code,
            headers=[("content-type", "text/html; charset=utf-8")],
            body=content.encode("utf-8"),
            media_type="text/html",
        )


__all__ = ["HTMLResponse"]
