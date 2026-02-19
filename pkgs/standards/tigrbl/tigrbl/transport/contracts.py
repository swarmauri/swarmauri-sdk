"""Transport-level request/response contract exports."""

from __future__ import annotations

from typing import Any

from .request import Request
from .response import Response


def get_header(request: Request, name: str, default: Any = None) -> Any:
    """Return a header value using case-insensitive request header mapping."""
    return request.headers.get(name, default)


__all__ = ["Request", "Response", "get_header"]
