"""Base middleware implementation supporting ASGI and WSGI."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from tigrbl.requests.adapters import request_from_asgi
from tigrbl.responses import Response

from .spec import ASGIApp, ASGIReceive, ASGISend, WSGIApp, WSGIStartResponse


class Middleware:
    """Base middleware for composing ASGI/WSGI pipelines."""

    def __init__(self, app: ASGIApp | WSGIApp, **kwargs: Any) -> None:
        self.app = app
        self.kwargs = kwargs

    async def asgi(
        self,
        scope: dict[str, Any],
        receive: ASGIReceive,
        send: ASGISend,
    ) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        body = await self._collect_body(receive)
        request = request_from_asgi(self, scope, body)

        async def call_next(_request: Any) -> Response:
            del _request
            replay_receive = self._build_replay_receive(body)
            return await self._call_downstream(scope, replay_receive)

        response = await self.dispatch(request, call_next)
        await self._send_response(send, response)

    async def dispatch(
        self,
        request: Any,
        call_next: Callable[[Any], Any],
    ) -> Any:
        return await call_next(request)

    @staticmethod
    async def _collect_body(receive: ASGIReceive) -> bytes:
        body = b""
        more_body = True
        while more_body:
            message = await receive()
            if message.get("type") != "http.request":
                continue
            body += message.get("body", b"")
            more_body = message.get("more_body", False)
        return body

    @staticmethod
    def _build_replay_receive(body: bytes) -> ASGIReceive:
        sent = False

        async def _replay_receive() -> dict[str, Any]:
            nonlocal sent
            if sent:
                return {"type": "http.disconnect"}
            sent = True
            return {"type": "http.request", "body": body, "more_body": False}

        return _replay_receive

    async def _call_downstream(
        self,
        scope: dict[str, Any],
        receive: ASGIReceive,
    ) -> Response:
        started: dict[str, Any] | None = None
        chunks: list[bytes] = []

        async def _capture_send(message: dict[str, Any]) -> None:
            nonlocal started
            message_type = message.get("type")
            if message_type == "http.response.start":
                started = message
                return
            if message_type == "http.response.body":
                chunks.append(message.get("body", b""))

        await self.app(scope, receive, _capture_send)

        if started is None:
            raise RuntimeError("No response returned.")

        headers = [
            (k.decode("latin-1"), v.decode("latin-1"))
            for k, v in started.get("headers", [])
        ]
        return Response(
            status_code=int(started.get("status", 200)),
            headers=headers,
            body=b"".join(chunks),
        )

    @staticmethod
    async def _send_response(send: ASGISend, response: Any) -> None:
        status_code = int(getattr(response, "status_code", 200))
        headers = getattr(response, "headers", [])
        body = getattr(response, "body", b"")

        if isinstance(headers, dict):
            header_items = list(headers.items())
        else:
            header_items = list(headers)

        encoded_headers = [
            (str(k).encode("latin-1"), str(v).encode("latin-1"))
            for k, v in header_items
        ]
        await send(
            {
                "type": "http.response.start",
                "status": status_code,
                "headers": encoded_headers,
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": body if isinstance(body, bytes) else bytes(body),
                "more_body": False,
            }
        )

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


class BaseHTTPMiddleware(Middleware):
    """Starlette-style HTTP middleware base for Tigrbl apps."""


__all__ = ["Middleware", "BaseHTTPMiddleware"]
