"""Dispatch-style HTTP middleware compatible with Tigrbl ASGI adapters."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any
from urllib.parse import parse_qs

from tigrbl.middlewares.middleware import Middleware
from tigrbl.requests import Request
from tigrbl.responses import Response

from .types import RequestResponseEndpoint


class BaseHTTPMiddleware(Middleware):
    """Middleware base class with a Starlette-like ``dispatch`` contract."""

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        return await call_next(request)

    async def asgi(
        self,
        scope: dict[str, Any],
        receive: Callable[[], Any],
        send: Callable[[dict[str, Any]], Any],
    ) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        request = await _request_from_scope(scope, receive)

        async def call_next(forward_request: Request) -> Response:
            message = {
                "body": forward_request.body,
                "sent": False,
            }
            response_state = {
                "status": None,
                "headers": [],
                "body": bytearray(),
            }

            async def downstream_receive() -> dict[str, Any]:
                if message["sent"]:
                    return {"type": "http.request", "body": b"", "more_body": False}
                message["sent"] = True
                return {
                    "type": "http.request",
                    "body": message["body"],
                    "more_body": False,
                }

            async def downstream_send(msg: dict[str, Any]) -> None:
                msg_type = msg.get("type")
                if msg_type == "http.response.start":
                    response_state["status"] = int(msg.get("status", 200))
                    response_state["headers"] = list(msg.get("headers", []))
                elif msg_type == "http.response.body":
                    response_state["body"].extend(msg.get("body", b""))

            await self.app(scope, downstream_receive, downstream_send)

            if response_state["status"] is None:
                raise RuntimeError("No response returned.")

            return Response(
                status_code=response_state["status"],
                headers=[
                    (k.decode("latin-1"), v.decode("latin-1"))
                    for k, v in response_state["headers"]
                ],
                body=bytes(response_state["body"]),
            )

        response = await self.dispatch(request, call_next)
        if response is None:
            raise RuntimeError("No response returned.")

        await send(
            {
                "type": "http.response.start",
                "status": response.status_code,
                "headers": [
                    (k.encode("latin-1"), v.encode("latin-1"))
                    for k, v in response.headers
                ],
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": response.body,
                "more_body": False,
            }
        )


async def _request_from_scope(scope: dict[str, Any], receive: Callable) -> Request:
    body = bytearray()
    more_body = True
    while more_body:
        message = await receive()
        body.extend(message.get("body", b""))
        more_body = bool(message.get("more_body", False))

    return Request(
        method=(scope.get("method") or "GET").upper(),
        path=scope.get("path") or "/",
        headers={
            key.decode("latin-1").lower(): value.decode("latin-1")
            for key, value in scope.get("headers", [])
        },
        query=parse_qs(
            (scope.get("query_string") or b"").decode("latin-1"),
            keep_blank_values=True,
        ),
        path_params={},
        body=bytes(body),
        script_name=scope.get("root_path", "") or "",
        scope=scope,
    )


__all__ = ["BaseHTTPMiddleware"]
