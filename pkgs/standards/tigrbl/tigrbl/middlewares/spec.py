"""Middleware protocol and callable type specs."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Protocol

Message = dict[str, Any]
ASGIReceive = Callable[[], Awaitable[Message]]
ASGISend = Callable[[Message], Awaitable[None]]
ASGIApp = Callable[[dict[str, Any], ASGIReceive, ASGISend], Awaitable[None]]
WSGIStartResponse = Callable[..., Any]
WSGIApp = Callable[[dict[str, Any], WSGIStartResponse], list[bytes]]


class MiddlewareSpec(Protocol):
    """Protocol for middleware classes compatible with ASGI and WSGI."""

    kwargs: dict[str, Any]

    async def asgi(
        self, scope: dict[str, Any], receive: ASGIReceive, send: ASGISend
    ) -> None: ...

    def wsgi(
        self, environ: dict[str, Any], start_response: WSGIStartResponse
    ) -> list[bytes]: ...
