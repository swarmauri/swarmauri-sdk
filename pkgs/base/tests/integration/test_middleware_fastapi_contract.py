import pytest
from fastapi import FastAPI, Request, Response
from httpx import ASGITransport, AsyncClient

from swarmauri_base.middlewares.CORSMiddleware import CORSMiddleware
from swarmauri_base.middlewares.MiddlewareBase import MiddlewareBase


class RewritePathMiddleware(MiddlewareBase):
    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        request.scope["path"] = "/rewritten"
        return await call_next(request)


class ShortCircuitMiddleware(MiddlewareBase):
    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        if request.method == "HEAD":
            return Response(content="head-should-not-send", media_type="text/plain")
        return Response(
            content="status-should-not-send",
            status_code=204,
            media_type="text/plain",
        )


@pytest.mark.asyncio
async def test_dispatch_forwarded_request_scope_is_used() -> None:
    app = FastAPI()

    @app.get("/rewritten")
    async def rewritten() -> dict[str, str]:
        return {"path": "rewritten"}

    wrapped_app = RewritePathMiddleware(app=app)

    transport = ASGITransport(app=wrapped_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/original")

    assert response.status_code == 200
    assert response.json() == {"path": "rewritten"}


@pytest.mark.asyncio
async def test_dispatch_normalizes_204_and_head_responses() -> None:
    app = FastAPI()

    @app.get("/")
    async def handler() -> dict[str, str]:
        return {"ok": "unused"}

    wrapped_app = ShortCircuitMiddleware(app=app)
    transport = ASGITransport(app=wrapped_app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        get_response = await client.get("/")
        head_response = await client.head("/")

    assert get_response.status_code == 204
    assert get_response.content == b""
    assert "content-length" not in get_response.headers
    assert "content-type" not in get_response.headers

    assert head_response.status_code == 200
    assert head_response.content == b""
    assert "content-length" not in head_response.headers
    assert "content-type" not in head_response.headers


@pytest.mark.asyncio
async def test_cors_middleware_handles_preflight_and_simple_requests() -> None:
    app = FastAPI()

    @app.get("/items")
    async def items() -> dict[str, str]:
        return {"ok": "yes"}

    wrapped_app = CORSMiddleware(
        app=app,
        allow_origins=["https://example.com"],
        allow_methods=["GET", "OPTIONS"],
        allow_headers=["x-api-key", "content-type"],
        expose_headers=["x-trace-id"],
        allow_credentials=True,
    )

    transport = ASGITransport(app=wrapped_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        preflight = await client.options(
            "/items",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "GET",
            },
        )
        simple = await client.get("/items", headers={"Origin": "https://example.com"})

    assert preflight.status_code == 204
    assert preflight.headers["access-control-allow-origin"] == "https://example.com"
    assert preflight.headers["access-control-allow-credentials"] == "true"

    assert simple.status_code == 200
    assert simple.headers["access-control-allow-origin"] == "https://example.com"
    assert simple.headers["access-control-expose-headers"] == "x-trace-id"
