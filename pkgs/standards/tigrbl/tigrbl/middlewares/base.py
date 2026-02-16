"""Request/response middleware base with ``dispatch`` + ``call_next`` semantics."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

from tigrbl.requests import Request
from tigrbl.requests.adapters import request_from_asgi
from tigrbl.responses import Response
from tigrbl.responses._transport import finalize_transport_response

from .middleware import Middleware
from .spec import ASGIReceive, ASGISend, Message


class BaseHTTPMiddleware(Middleware):
    """Base middleware for intercepting HTTP requests in ASGI mode."""

    async def dispatch(
        self,
        request: Request,
        call_next: Any,
    ) -> Response:
        """Process the request and optionally delegate to downstream middleware/app."""

        return await call_next(request)

    @staticmethod
    def _scope_from_request(scope: dict[str, Any], request: Request) -> dict[str, Any]:
        query_string = urlencode(
            [
                (name, value)
                for name, values in request.query.items()
                for value in values
            ],
            doseq=True,
        ).encode("latin-1")
        return {
            **scope,
            "method": request.method,
            "path": request.path,
            "query_string": query_string,
            "headers": [
                (key.encode("latin-1"), value.encode("latin-1"))
                for key, value in request.headers.items()
            ],
            "root_path": request.script_name,
        }

    async def asgi(
        self,
        scope: dict[str, Any],
        receive: ASGIReceive,
        send: ASGISend,
    ) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        request_body = b""
        more_body = True
        while more_body:
            message = await receive()
            request_body += message.get("body", b"")
            more_body = message.get("more_body", False)

        request = request_from_asgi(None, scope, request_body)

        async def call_next(forward_request: Request | None = None) -> Response:
            target_request = forward_request or request
            target_scope = self._scope_from_request(scope, target_request)

            messages: list[Message] = []
            body_sent = False

            async def receive_for_app() -> Message:
                nonlocal body_sent
                if body_sent:
                    return {"type": "http.request", "body": b"", "more_body": False}
                body_sent = True
                return {
                    "type": "http.request",
                    "body": target_request.body,
                    "more_body": False,
                }

            async def send_from_app(message: Message) -> None:
                messages.append(message)

            await self.app(target_scope, receive_for_app, send_from_app)

            start = next(
                message
                for message in messages
                if message.get("type") == "http.response.start"
            )
            raw_headers = list(start.get("headers", []))
            body = b"".join(
                message.get("body", b"")
                for message in messages
                if message.get("type") == "http.response.body"
            )
            headers, finalized_body = finalize_transport_response(
                target_scope,
                int(start.get("status", 200)),
                raw_headers,
                body,
            )
            return Response(
                status_code=int(start.get("status", 200)),
                headers=[
                    (key.decode("latin-1"), value.decode("latin-1"))
                    for key, value in headers
                ],
                body=finalized_body,
            )

        response = await self.dispatch(request, call_next)
        headers, finalized_body = finalize_transport_response(
            scope,
            response.status_code,
            response.raw_headers,
            response.body,
        )
        await send(
            {
                "type": "http.response.start",
                "status": response.status_code,
                "headers": headers,
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": finalized_body,
                "more_body": False,
            }
        )


__all__ = ["BaseHTTPMiddleware"]
