"""Concrete redirect response primitive."""

from __future__ import annotations

from ._response import Response


class RedirectResponse(Response):
    def __init__(self, url: str, status_code: int = 307) -> None:
        super().__init__(
            status_code=status_code,
            headers=[("location", url)],
            body=b"",
            media_type=None,
        )
        self.url = url


__all__ = ["RedirectResponse"]
