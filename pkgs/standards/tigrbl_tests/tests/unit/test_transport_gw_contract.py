from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from tigrbl.transport.gw import asgi_app
from tigrbl.transport.response import Response


@pytest.mark.asyncio
async def test_asgi_gateway_roundtrip_smoke() -> None:
    async def _dispatch(_req):
        return Response.json({"ok": True}, status_code=200)

    router = SimpleNamespace(_dispatch=_dispatch, _middlewares=[], debug=False)
    sent: list[dict[str, object]] = []

    receive_messages = iter(
        [{"type": "http.request", "body": b"{}", "more_body": False}]
    )

    async def receive() -> dict[str, object]:
        return next(receive_messages)

    async def send(message: dict[str, object]) -> None:
        sent.append(message)

    await asgi_app(
        router,
        {
            "type": "http",
            "method": "POST",
            "path": "/ping",
            "query_string": b"",
            "headers": [],
        },
        receive,
        send,
    )

    assert sent[0]["type"] == "http.response.start"
    assert sent[0]["status"] == 200
    assert sent[1]["type"] == "http.response.body"
    assert json.loads(sent[1]["body"]) == {"ok": True}


@pytest.mark.asyncio
async def test_asgi_gateway_middleware_order_and_short_circuit() -> None:
    events: list[str] = []

    async def _dispatch(_req):
        events.append("dispatch")
        return Response.json({"ok": True}, status_code=200)

    class OuterMiddleware:
        def __init__(self, app, **_):
            self.app = app

        async def __call__(self, scope, receive, send):
            events.append("outer:before")
            await self.app(scope, receive, send)
            events.append("outer:after")

    class InnerMiddleware:
        def __init__(self, app, short_circuit: bool = False, **_):
            self.app = app
            self.short_circuit = short_circuit

        async def __call__(self, scope, receive, send):
            events.append("inner:before")
            if self.short_circuit:
                await send(
                    {"type": "http.response.start", "status": 204, "headers": []}
                )
                await send(
                    {"type": "http.response.body", "body": b"", "more_body": False}
                )
                events.append("inner:short")
                return
            await self.app(scope, receive, send)
            events.append("inner:after")

    router = SimpleNamespace(
        _dispatch=_dispatch,
        _middlewares=[
            (OuterMiddleware, {}),
            (InnerMiddleware, {"short_circuit": False}),
        ],
        debug=False,
    )

    receive_messages = iter([{"type": "http.request", "body": b"", "more_body": False}])
    sent: list[dict[str, object]] = []

    async def receive() -> dict[str, object]:
        return next(receive_messages)

    async def send(message: dict[str, object]) -> None:
        sent.append(message)

    await asgi_app(
        router,
        {
            "type": "http",
            "method": "GET",
            "path": "/",
            "query_string": b"",
            "headers": [],
        },
        receive,
        send,
    )

    assert events == [
        "outer:before",
        "inner:before",
        "dispatch",
        "inner:after",
        "outer:after",
    ]
    assert sent[0]["status"] == 200

    events.clear()
    sent.clear()
    router._middlewares = [
        (OuterMiddleware, {}),
        (InnerMiddleware, {"short_circuit": True}),
    ]
    receive_messages = iter([{"type": "http.request", "body": b"", "more_body": False}])

    await asgi_app(
        router,
        {
            "type": "http",
            "method": "GET",
            "path": "/",
            "query_string": b"",
            "headers": [],
        },
        receive,
        send,
    )

    assert events == ["outer:before", "inner:before", "inner:short", "outer:after"]
    assert sent[0]["status"] == 204
