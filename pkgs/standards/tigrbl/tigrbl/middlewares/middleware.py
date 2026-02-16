"""Base middleware implementation supporting ASGI and WSGI."""

from __future__ import annotations

from typing import Any

from .spec import ASGIApp, ASGIReceive, ASGISend, Message, WSGIApp, WSGIStartResponse


class Middleware:
    """Base middleware for composing ASGI/WSGI pipelines."""

    def __init__(self, app: ASGIApp | WSGIApp, **kwargs: Any) -> None:
        self.app = app
        self.kwargs = kwargs

    async def asgi(
        self,
        scope: Message,
        receive: ASGIReceive,
        send: ASGISend,
    ) -> None:
        await self.app(scope, receive, send)

    def wsgi(
        self,
        environ: dict[str, Any],
        start_response: WSGIStartResponse,
    ) -> list[bytes]:
        return self.app(environ, start_response)

    def __call__(self, *args: Any, **kwargs: Any):
        if len(args) == 3 and isinstance(args[0], dict):
            return self.asgi(args[0], args[1], args[2])
        if len(args) == 2 and isinstance(args[0], dict):
            return self.wsgi(args[0], args[1])
        raise TypeError("Invalid middleware invocation")
