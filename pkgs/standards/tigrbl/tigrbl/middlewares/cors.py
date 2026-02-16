"""CORS middleware for ASGI/WSGI adapters."""

from __future__ import annotations

from typing import Any

from tigrbl.headers import Headers
from tigrbl.requests import Request
from tigrbl.responses import Response

from .base import BaseHTTPMiddleware
from .spec import WSGIStartResponse


class CORSMiddleware(BaseHTTPMiddleware):
    _CORS_HEADER_NAMES = {
        "access-control-allow-origin",
        "access-control-allow-methods",
        "access-control-allow-headers",
        "access-control-max-age",
        "access-control-allow-credentials",
        "vary",
    }

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

    def _resolve_allow_origin(self, request_headers: Headers) -> str:
        origin = request_headers.get("origin")
        if self.allow_origin == "*" or not origin:
            return self.allow_origin
        allowed = [candidate.strip() for candidate in self.allow_origin.split(",")]
        if origin in allowed:
            return origin
        return "null"

    def _cors_headers(self, request_headers: Headers) -> list[tuple[str, str]]:
        allow_origin = self._resolve_allow_origin(request_headers)
        allow_headers = self.allow_headers
        requested_headers = request_headers.get("access-control-request-headers")
        if allow_headers == "*" and requested_headers:
            allow_headers = requested_headers

        headers = [
            ("access-control-allow-origin", allow_origin),
            ("access-control-allow-methods", self.allow_methods),
            ("access-control-allow-headers", allow_headers),
            ("access-control-max-age", str(self.max_age)),
            ("vary", "origin"),
        ]
        if self.allow_credentials:
            headers.append(("access-control-allow-credentials", "true"))
        return headers

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        request_headers = Headers(request.headers)
        is_preflight = (
            request.method.upper() == "OPTIONS"
            and request_headers.get("origin") is not None
            and request_headers.get("access-control-request-method") is not None
        )

        if is_preflight:
            return Response(
                status_code=204,
                headers=self._cors_headers(request_headers),
                body=b"",
            )

        response = await call_next(request)
        response_headers = response.headers_map
        for key, value in self._cors_headers(request_headers):
            response_headers[key] = value
        response.headers = response_headers.as_list()
        return response

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

        request_headers = Headers(
            {
                "origin": str(environ.get("HTTP_ORIGIN") or ""),
                "access-control-request-headers": str(
                    environ.get("HTTP_ACCESS_CONTROL_REQUEST_HEADERS") or ""
                ),
            }
        )

        if is_preflight:
            start_response("204 No Content", self._cors_headers(request_headers))
            return [b""]

        def cors_start_response(
            status: str, headers: list[tuple[str, str]], *args: Any
        ):
            merged = [
                (key, value)
                for key, value in headers
                if key.lower() not in self._CORS_HEADER_NAMES
            ]
            for key, value in self._cors_headers(request_headers):
                merged.append((key, value))
            return start_response(status, merged, *args)

        return self.app(environ, cors_start_response)


__all__ = ["CORSMiddleware"]
