from typing import Any

import pytest
from fastapi import FastAPI
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.responses import JSONResponse
from starlette.routing import Route

from swarmauri_middleware_tracetiming import TraceTimingMiddleware


async def _invoke_http_app(
    app: Any,
    path: str,
    headers: list[tuple[bytes, bytes]] | None = None,
) -> dict[str, Any]:
    sent_messages: list[dict[str, Any]] = []
    received = False

    async def receive() -> dict[str, Any]:
        nonlocal received
        if not received:
            received = True
            return {"type": "http.request", "body": b"", "more_body": False}
        return {"type": "http.disconnect"}

    async def send(message: dict[str, Any]) -> None:
        sent_messages.append(message)

    scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.3"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": path,
        "raw_path": path.encode("latin-1"),
        "query_string": b"",
        "headers": headers or [],
        "client": ("127.0.0.1", 50000),
        "server": ("testserver", 80),
    }

    await app(scope, receive, send)

    response_start = next(
        msg for msg in sent_messages if msg["type"] == "http.response.start"
    )
    return {
        "status": response_start["status"],
        "headers": {
            k.decode("latin-1"): v.decode("latin-1")
            for k, v in response_start.get("headers", [])
        },
    }


class TestFrameworkIntegration:
    @pytest.mark.asyncio
    async def test_fastapi_middleware_integration(self) -> None:
        app = FastAPI()
        app.add_middleware(TraceTimingMiddleware, edge_ms_getter=lambda _: 7.5)

        @app.get("/health")
        async def health() -> dict[str, str]:
            return {"status": "ok"}

        response = await _invoke_http_app(
            app,
            "/health",
            headers=[
                (
                    b"traceparent",
                    b"00-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-bbbbbbbbbbbbbbbb-01",
                ),
                (b"tracestate", b"vendor=foo"),
            ],
        )

        assert response["status"] == 200
        assert response["headers"]["traceparent"] == (
            "00-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-bbbbbbbbbbbbbbbb-01"
        )
        assert response["headers"]["tracestate"] == "vendor=foo"
        assert "server-timing" in response["headers"]
        assert "app;dur=" in response["headers"]["server-timing"]
        assert "edge;dur=7.5" in response["headers"]["server-timing"]
        assert response["headers"]["timing-allow-origin"] == "*"

    @pytest.mark.asyncio
    async def test_starlette_middleware_integration(self) -> None:
        async def homepage(_request: Any) -> JSONResponse:
            return JSONResponse({"hello": "starlette"})

        app = Starlette(
            routes=[Route("/", endpoint=homepage)],
            middleware=[
                Middleware(TraceTimingMiddleware, edge_ms_getter=lambda _: 2.0)
            ],
        )

        response = await _invoke_http_app(app, "/")

        assert response["status"] == 200
        assert "traceparent" in response["headers"]
        assert response["headers"]["traceparent"].startswith("00-")
        assert "server-timing" in response["headers"]
        assert "app;dur=" in response["headers"]["server-timing"]
        assert "edge;dur=2.0" in response["headers"]["server-timing"]
        assert response["headers"]["timing-allow-origin"] == "*"
