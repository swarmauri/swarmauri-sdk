"""CORS middleware for ASGI/WSGI adapters."""

from __future__ import annotations

from typing import Any
import re

from tigrbl._concrete._headers import Headers
from tigrbl.requests import Request
from tigrbl._concrete._response import Response

from .base import BaseHTTPMiddleware
from ..specs.middleware_spec import WSGIStartResponse


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
        allow_origins: list[str] | tuple[str, ...] | None = None,
        allow_origin_regex: str | None = None,
        allow_methods: str
        | list[str]
        | tuple[str, ...] = "GET,POST,PUT,PATCH,DELETE,OPTIONS",
        allow_headers: str | list[str] | tuple[str, ...] = "*",
        allow_credentials: bool = False,
        max_age: int = 600,
    ) -> None:
        super().__init__(
            app,
            allow_origin=allow_origin,
            allow_origins=allow_origins,
            allow_origin_regex=allow_origin_regex,
            allow_methods=allow_methods,
            allow_headers=allow_headers,
            allow_credentials=allow_credentials,
            max_age=max_age,
        )
        self.allow_origin = allow_origin
        self.allow_origins = list(allow_origins or [])
        self.allow_origin_regex = allow_origin_regex
        self._allow_origin_pattern = (
            re.compile(allow_origin_regex) if allow_origin_regex else None
        )
        self.allow_methods = self._normalize_listish(allow_methods)
        self.allow_headers = self._normalize_listish(allow_headers)
        self.allow_credentials = allow_credentials
        self.max_age = max_age

    @staticmethod
    def _normalize_listish(value: str | list[str] | tuple[str, ...]) -> str:
        if isinstance(value, str):
            return value
        return ",".join(item.strip() for item in value)

    def _resolve_allow_origin(self, request_headers: Headers) -> str:
        origin = request_headers.get("origin")
        if not origin:
            return self.allow_origin

        if self._allow_origin_pattern and self._allow_origin_pattern.match(origin):
            return origin

        if self.allow_origins:
            if origin in self.allow_origins:
                return origin
            return "null"

        if self.allow_origin == "*":
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




__all__ = ["CORSMiddleware"]
