"""CORS middleware for ASGI/WSGI adapters."""

from __future__ import annotations

from typing import Any

from tigrbl.header import Headers

from .middleware import Middleware
from .spec import ASGIReceive, ASGISend, WSGIStartResponse


class CORSMiddleware(Middleware):
    def __init__(
        self,
        app,
        *,
        allow_origin: str = "*",
        allow_methods: str = "GET,POST,PUT,PATCH,DELETE,OPTIONS",
        allow_headers: str = "*",
        allow_credentials: bool = False,
        max_age: int = 600,
    ) -> None:
        super().__init__(
            app,
            allow_origin=allow_origin,
            allow_methods=allow_methods,
            allow_headers=allow_headers,
            allow_credentials=allow_credentials,
            max_age=max_age,
        )
        self.allow_origin = allow_origin
        self.allow_methods = allow_methods
        self.allow_headers = allow_headers
        self.allow_credentials = allow_credentials
        self.max_age = max_age

    def _cors_headers(self) -> list[tuple[str, str]]:
        headers = [
            ("access-control-allow-origin", self.allow_origin),
            ("access-control-allow-methods", self.allow_methods),
            ("access-control-allow-headers", self.allow_headers),
            ("access-control-max-age", str(self.max_age)),
        ]
        if self.allow_credentials:
            headers.append(("access-control-allow-credentials", "true"))
        return headers

    async def asgi(
        self,
        scope: dict[str, Any],
        receive: ASGIReceive,
        send: ASGISend,
    ) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        request_headers = Headers(
            [
                (k.decode("latin-1"), v.decode("latin-1"))
                for k, v in scope.get("headers", [])
            ]
        )
        is_preflight = (
            (scope.get("method") or "").upper() == "OPTIONS"
            and request_headers.get("origin") is not None
            and request_headers.get("access-control-request-method") is not None
        )
        if is_preflight:
            await send(
                {
                    "type": "http.response.start",
                    "status": 204,
                    "headers": [
                        (k.encode("latin-1"), v.encode("latin-1"))
                        for k, v in self._cors_headers()
                    ],
                }
            )
            await send({"type": "http.response.body", "body": b""})
            return

        async def send_with_cors(message: dict[str, Any]) -> None:
            if message.get("type") == "http.response.start":
                headers = list(message.get("headers", []))
                headers.extend(
                    [
                        (k.encode("latin-1"), v.encode("latin-1"))
                        for k, v in self._cors_headers()
                    ]
                )
                message = {**message, "headers": headers}
            await send(message)

        await self.app(scope, receive, send_with_cors)

    def wsgi(
        self,
        environ: dict[str, Any],
        start_response: WSGIStartResponse,
    ) -> list[bytes]:
        method = (environ.get("REQUEST_METHOD") or "").upper()
        is_preflight = (
            method == "OPTIONS"
            and environ.get("HTTP_ORIGIN")
            and environ.get("HTTP_ACCESS_CONTROL_REQUEST_METHOD")
        )

        if is_preflight:
            start_response("204 No Content", self._cors_headers())
            return [b""]

        def cors_start_response(
            status: str, headers: list[tuple[str, str]], *args: Any
        ):
            merged = list(headers) + self._cors_headers()
            return start_response(status, merged, *args)

        return self.app(environ, cors_start_response)


__all__ = ["CORSMiddleware"]
