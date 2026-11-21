import pytest
from httpx import ASGITransport, AsyncClient
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from swarmauri_core.middlewares.IMiddleware import ASGIApp, Message, Scope

from swarmauri_base.middlewares.MiddlewareBase import MiddlewareBase


class TrackingMiddleware(MiddlewareBase):
    """Record middleware hook order in a Starlette stack."""

    def __init__(self, app: ASGIApp, tracker: list[str]):
        super().__init__(app=app)
        self.tracker = tracker

    async def on_scope(self, scope: Scope) -> Scope:
        self.tracker.append("on_scope")
        return scope

    async def on_receive(self, scope: Scope, message: Message) -> Message:
        self.tracker.append(f"on_receive:{message['type']}")
        return message

    async def on_send(self, scope: Scope, message: Message) -> Message:
        self.tracker.append(f"on_send:{message['type']}")
        return message

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        self.tracker.append("dispatch:before_call_next")
        response = await call_next(request)
        self.tracker.append("dispatch:after_call_next")
        response.headers["X-Tracking"] = ",".join(self.tracker)
        return response


async def echo(request: Request) -> JSONResponse:
    return JSONResponse({"payload": await request.json()})


@pytest.mark.asyncio
async def test_middleware_wrapping_starlette_app() -> None:
    tracker: list[str] = []
    app = Starlette(routes=[Route("/echo", echo, methods=["POST"])])
    wrapped_app = TrackingMiddleware(app=app, tracker=tracker)

    transport = ASGITransport(app=wrapped_app)
    async with AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.post("/echo", json={"value": "decorated"})

    assert response.status_code == 200
    assert response.json() == {"payload": {"value": "decorated"}}
    tracking_header = response.headers["X-Tracking"].split(",")
    assert tracking_header[0] == "on_scope"
    assert tracking_header[1] == "dispatch:before_call_next"
    assert tracking_header[-1] == "dispatch:after_call_next"
    assert tracking_header[2:-1]
    assert all(
        entry.startswith("on_receive:") for entry in tracking_header[2:-1]
    )
    assert any(
        entry == "on_receive:http.request" for entry in tracking_header[2:-1]
    )
    assert tracker == tracking_header + [
        "on_send:http.response.start",
        "on_send:http.response.body",
    ]


@pytest.mark.asyncio
async def test_middleware_added_to_starlette_stack() -> None:
    tracker: list[str] = []
    app = Starlette(routes=[Route("/echo", echo, methods=["POST"])])
    app.add_middleware(TrackingMiddleware, tracker=tracker)

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.post("/echo", json={"value": "added"})

    assert response.status_code == 200
    assert response.json() == {"payload": {"value": "added"}}
    tracking_header = response.headers["X-Tracking"].split(",")
    assert tracking_header[0] == "on_scope"
    assert tracking_header[1] == "dispatch:before_call_next"
    assert tracking_header[-1] == "dispatch:after_call_next"
    assert tracking_header[2:-1]
    assert all(
        entry.startswith("on_receive:") for entry in tracking_header[2:-1]
    )
    assert any(
        entry == "on_receive:http.request" for entry in tracking_header[2:-1]
    )
    assert tracker == tracking_header + [
        "on_send:http.response.start",
        "on_send:http.response.body",
    ]
