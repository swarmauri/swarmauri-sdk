from __future__ import annotations

from typing import Any, Iterable

from swarmauri_base.middlewares.MiddlewareBase import MiddlewareBase
from swarmauri_core.middlewares.IMiddleware import Scope


class CORSMiddleware(MiddlewareBase):
    """ASGI CORS middleware with preflight handling and response header injection."""

    def __init__(
        self,
        app=None,
        *,
        allow_origins: Iterable[str] | None = None,
        allow_methods: Iterable[str] | None = None,
        allow_headers: Iterable[str] | None = None,
        expose_headers: Iterable[str] | None = None,
        allow_credentials: bool = False,
        max_age: int = 600,
    ) -> None:
        super().__init__(app=app)
        self.allow_origins = tuple(allow_origins or ("*",))
        self.allow_methods = tuple(
            allow_methods or ("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS")
        )
        self.allow_headers = tuple(allow_headers or ("*",))
        self.expose_headers = tuple(expose_headers or ())
        self.allow_credentials = allow_credentials
        self.max_age = max_age

    def _join(self, values: Iterable[str]) -> str:
        return ", ".join(values)

    def _allow_origin_value(self, request_origin: str | None) -> str:
        if "*" in self.allow_origins and not self.allow_credentials:
            return "*"
        if request_origin and (
            "*" in self.allow_origins or request_origin in self.allow_origins
        ):
            return request_origin
        return "null"

    def _cors_headers(self, scope: Scope) -> list[tuple[bytes, bytes]]:
        raw_headers = {
            k.decode("latin-1").lower(): v.decode("latin-1")
            for k, v in scope.get("headers", [])
        }
        origin = raw_headers.get("origin")

        headers: list[tuple[str, str]] = [
            ("access-control-allow-origin", self._allow_origin_value(origin)),
            ("access-control-allow-methods", self._join(self.allow_methods)),
            ("access-control-allow-headers", self._join(self.allow_headers)),
            ("access-control-max-age", str(self.max_age)),
            ("vary", "origin"),
        ]
        if self.allow_credentials:
            headers.append(("access-control-allow-credentials", "true"))
        if self.expose_headers:
            headers.append(
                ("access-control-expose-headers", self._join(self.expose_headers))
            )

        return [(k.encode("latin-1"), v.encode("latin-1")) for k, v in headers]

    async def __call__(self, scope, receive, send) -> None:  # type: ignore[override]
        if scope.get("type") != "http":
            await super().__call__(scope, receive, send)
            return

        method = str(scope.get("method", "")).upper()
        headers = {
            k.decode("latin-1").lower(): v.decode("latin-1")
            for k, v in scope.get("headers", [])
        }
        is_preflight = (
            method == "OPTIONS"
            and headers.get("origin") is not None
            and headers.get("access-control-request-method") is not None
        )

        if is_preflight:
            cors_headers = self._cors_headers(scope)
            await send(
                {
                    "type": "http.response.start",
                    "status": 204,
                    "headers": cors_headers,
                }
            )
            await send(
                {
                    "type": "http.response.body",
                    "body": b"",
                    "more_body": False,
                }
            )
            return

        async def send_with_cors(message: dict[str, Any]) -> None:
            if message.get("type") == "http.response.start":
                existing = list(message.get("headers", []))
                message = {
                    **message,
                    "headers": existing + self._cors_headers(scope),
                }
            await send(message)

        await super().__call__(scope, receive, send_with_cors)
