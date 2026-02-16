from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware as StarletteBaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.responses import PlainTextResponse as StarlettePlainTextResponse
from starlette.responses import Response as StarletteResponse
from starlette.routing import Route

from tigrbl import TigrblApp
from tigrbl.middleware import BaseHTTPMiddleware
from tigrbl.requests import Request
from tigrbl.responses import Response


class TigrblHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers.append(("x-parity", "tigrbl"))
        return response


class StarletteHeaderMiddleware(StarletteBaseHTTPMiddleware):
    async def dispatch(self, request: StarletteRequest, call_next):
        response = await call_next(request)
        response.headers["x-parity"] = "tigrbl"
        return response


class TigrblShortCircuitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/blocked":
            return Response.text("blocked", status_code=403)
        return await call_next(request)


class StarletteShortCircuitMiddleware(StarletteBaseHTTPMiddleware):
    async def dispatch(self, request: StarletteRequest, call_next):
        if request.url.path == "/blocked":
            return StarlettePlainTextResponse("blocked", status_code=403)
        return await call_next(request)


class TigrblBodyProbeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        body_size = len(request.body)
        response = await call_next(request)
        response.headers.append(("x-body-size", str(body_size)))
        return response


class StarletteBodyProbeMiddleware(StarletteBaseHTTPMiddleware):
    async def dispatch(self, request: StarletteRequest, call_next):
        body_size = len(await request.body())
        response = await call_next(request)
        response.headers["x-body-size"] = str(body_size)
        return response


@pytest.mark.asyncio()
async def test_base_http_middleware_header_injection_matches_starlette() -> None:
    tigrbl_app = TigrblApp()

    @tigrbl_app.get("/ok")
    async def tigrbl_ok() -> Response:
        return Response.text("ok")

    tigrbl_app.add_middleware(TigrblHeaderMiddleware)

    async def starlette_ok(request: StarletteRequest) -> StarletteResponse:
        del request
        return StarlettePlainTextResponse("ok")

    starlette_app = Starlette(routes=[Route("/ok", endpoint=starlette_ok)])
    starlette_app.add_middleware(StarletteHeaderMiddleware)

    async with (
        AsyncClient(
            transport=ASGITransport(app=tigrbl_app),
            base_url="http://test",
        ) as t_client,
        AsyncClient(
            transport=ASGITransport(app=starlette_app),
            base_url="http://test",
        ) as s_client,
    ):
        t_resp = await t_client.get("/ok")
        s_resp = await s_client.get("/ok")

    assert t_resp.status_code == s_resp.status_code == 200
    assert t_resp.text == s_resp.text == "ok"
    assert t_resp.headers["x-parity"] == s_resp.headers["x-parity"] == "tigrbl"


@pytest.mark.asyncio()
async def test_base_http_middleware_short_circuit_matches_starlette() -> None:
    tigrbl_app = TigrblApp()

    @tigrbl_app.get("/blocked")
    async def tigrbl_blocked() -> Response:
        return Response.text("should-not-run")

    tigrbl_app.add_middleware(TigrblShortCircuitMiddleware)

    async def starlette_blocked(request: StarletteRequest) -> StarletteResponse:
        del request
        return StarlettePlainTextResponse("should-not-run")

    starlette_app = Starlette(routes=[Route("/blocked", endpoint=starlette_blocked)])
    starlette_app.add_middleware(StarletteShortCircuitMiddleware)

    async with (
        AsyncClient(
            transport=ASGITransport(app=tigrbl_app),
            base_url="http://test",
        ) as t_client,
        AsyncClient(
            transport=ASGITransport(app=starlette_app),
            base_url="http://test",
        ) as s_client,
    ):
        t_resp = await t_client.get("/blocked")
        s_resp = await s_client.get("/blocked")

    assert t_resp.status_code == s_resp.status_code == 403
    assert t_resp.text == s_resp.text == "blocked"


@pytest.mark.asyncio()
async def test_base_http_middleware_body_read_and_forward_matches_starlette() -> None:
    tigrbl_app = TigrblApp()

    @tigrbl_app.post("/echo")
    async def tigrbl_echo(request: Request) -> Response:
        return Response.text(request.body.decode("utf-8"))

    tigrbl_app.add_middleware(TigrblBodyProbeMiddleware)

    async def starlette_echo(request: StarletteRequest) -> StarletteResponse:
        return StarlettePlainTextResponse((await request.body()).decode("utf-8"))

    starlette_app = Starlette(
        routes=[Route("/echo", endpoint=starlette_echo, methods=["POST"])]
    )
    starlette_app.add_middleware(StarletteBodyProbeMiddleware)

    payload = "hello-middlewares"
    async with (
        AsyncClient(
            transport=ASGITransport(app=tigrbl_app),
            base_url="http://test",
        ) as t_client,
        AsyncClient(
            transport=ASGITransport(app=starlette_app),
            base_url="http://test",
        ) as s_client,
    ):
        t_resp = await t_client.post("/echo", content=payload)
        s_resp = await s_client.post("/echo", content=payload)

    assert t_resp.status_code == s_resp.status_code == 200
    assert t_resp.text == s_resp.text == payload
    assert (
        t_resp.headers["x-body-size"]
        == s_resp.headers["x-body-size"]
        == str(len(payload))
    )
