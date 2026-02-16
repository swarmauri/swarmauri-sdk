"""Type aliases for dispatch-style middleware."""

from __future__ import annotations

from collections.abc import Callable, Awaitable

from tigrbl.requests import Request
from tigrbl.responses import Response

RequestResponseEndpoint = Callable[[Request], Awaitable[Response]]

__all__ = ["RequestResponseEndpoint"]
