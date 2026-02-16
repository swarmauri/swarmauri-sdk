from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

pytest.importorskip("starlette")

from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware as StarletteBaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.responses import JSONResponse as StarletteJSONResponse
from starlette.routing import Route

from tigrbl.app.tigrbl_app import TigrblApp
from tigrbl.middleware import BaseHTTPMiddleware


class TigrblTrackingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, tracker: list[str]):
        super().__init__(app)
        self.tracker = tracker

    async def dispatch(self, request, call_next):
        payload = await request.json()
        self.tracker.append(
            f"before:{request.method}:{request.url.path}:{payload['value']}"
        )
        response = await call_next(request)
        response.headers.append(("x-tracker", "tigrbl"))
        self.tracker.append("after")
        return response


class StarletteTrackingMiddleware(StarletteBaseHTTPMiddleware):
    def __init__(self, app, tracker: list[str]):
        super().__init__(app)
        self.tracker = tracker

    async def dispatch(self, request: StarletteRequest, call_next):
        payload = await request.json()
        self.tracker.append(
            f"before:{request.method}:{request.url.path}:{payload['value']}"
        )
        response = await call_next(request)
        response.headers["x-tracker"] = "starlette"
        self.tracker.append("after")
        return response


@pytest.mark.asyncio
async def test_tigrbl_base_http_middleware_dispatch_contract() -> None:
    tracker: list[str] = []
    app = TigrblApp()

    @app.post("/echo")
    async def echo(request):
        payload = await request.json()
        return {"value": payload["value"]}

    app.add_middleware(TigrblTrackingMiddleware, tracker=tracker)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post("/echo", json={"value": "ok"})

    assert response.status_code == 200
    assert response.json() == {"value": "ok"}
    assert response.headers["x-tracker"] == "tigrbl"
    assert tracker == ["before:POST:/echo:ok", "after"]


@pytest.mark.asyncio
async def test_tigrbl_and_starlette_middleware_observe_same_request_lifecycle() -> None:
    tigrbl_tracker: list[str] = []
    starlette_tracker: list[str] = []

    tigrbl_app = TigrblApp()

    @tigrbl_app.post("/echo")
    async def tigrbl_echo(request):
        payload = await request.json()
        return {"value": payload["value"]}

    tigrbl_app.add_middleware(TigrblTrackingMiddleware, tracker=tigrbl_tracker)

    async def starlette_echo(request: StarletteRequest):
        payload = await request.json()
        return StarletteJSONResponse({"value": payload["value"]})

    starlette_app = Starlette(
        routes=[Route("/echo", endpoint=starlette_echo, methods=["POST"])]
    )
    starlette_app.add_middleware(StarletteTrackingMiddleware, tracker=starlette_tracker)

    tigrbl_transport = ASGITransport(app=tigrbl_app)
    starlette_transport = ASGITransport(app=starlette_app)

    async with AsyncClient(
        transport=tigrbl_transport, base_url="http://testserver"
    ) as tigrbl_client:
        tigrbl_response = await tigrbl_client.post("/echo", json={"value": "parity"})

    async with AsyncClient(
        transport=starlette_transport, base_url="http://testserver"
    ) as starlette_client:
        starlette_response = await starlette_client.post(
            "/echo", json={"value": "parity"}
        )

    assert tigrbl_response.status_code == starlette_response.status_code == 200
    assert tigrbl_response.json() == starlette_response.json() == {"value": "parity"}
    assert tigrbl_response.headers["x-tracker"] == "tigrbl"
    assert starlette_response.headers["x-tracker"] == "starlette"
    assert tigrbl_tracker == starlette_tracker == ["before:POST:/echo:parity", "after"]
