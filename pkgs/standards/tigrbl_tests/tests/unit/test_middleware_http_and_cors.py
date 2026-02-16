from __future__ import annotations

import pytest

from tigrbl.middlewares import BaseHTTPMiddleware, CORSMiddleware
from tigrbl.requests import Request
from tigrbl.responses import Response


async def _run_asgi(app, scope: dict, body: bytes = b"") -> list[dict]:
    sent: list[dict] = []
    emitted = False

    async def receive() -> dict:
        nonlocal emitted
        if emitted:
            return {"type": "http.request", "body": b"", "more_body": False}
        emitted = True
        return {"type": "http.request", "body": body, "more_body": False}

    async def send(message: dict) -> None:
        sent.append(message)

    await app(scope, receive, send)
    return sent


class RewriteMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rewritten = Request(
            method="POST",
            path="/rewritten",
            headers={**request.headers, "x-forwarded": "yes"},
            query={"changed": ["1"]},
            path_params={},
            body=b"forwarded",
            script_name="",
            scope=request.scope,
        )
        return await call_next(rewritten)


@pytest.mark.asyncio
async def test_base_http_middleware_call_next_uses_forwarded_scope_and_body() -> None:
    async def endpoint(scope, receive, send):
        body_msg = await receive()
        payload = (
            f"{scope.get('method')}|{scope.get('path')}|"
            f"{scope.get('query_string', b'').decode('latin-1')}|"
            f"{dict((k.decode('latin-1'), v.decode('latin-1')) for k, v in scope['headers'])['x-forwarded']}|"
            f"{body_msg.get('body', b'').decode('latin-1')}"
        ).encode("utf-8")
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [(b"content-type", b"text/plain")],
            }
        )
        await send({"type": "http.response.body", "body": payload, "more_body": False})

    app = RewriteMiddleware(endpoint)
    messages = await _run_asgi(
        app,
        {
            "type": "http",
            "method": "GET",
            "path": "/original",
            "query_string": b"before=1",
            "headers": [(b"host", b"test")],
        },
        body=b"ignored",
    )

    body = next(m for m in messages if m["type"] == "http.response.body")["body"]
    assert body == b"POST|/rewritten|changed=1|yes|forwarded"


class ShortCircuitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        return Response.text("should-be-stripped", status_code=204)


@pytest.mark.asyncio
async def test_base_http_middleware_normalizes_no_body_responses() -> None:
    async def endpoint(scope, receive, send):
        del scope, receive
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"ok", "more_body": False})

    app = ShortCircuitMiddleware(endpoint)
    messages = await _run_asgi(
        app,
        {
            "type": "http",
            "method": "GET",
            "path": "/",
            "query_string": b"",
            "headers": [],
        },
    )

    start = next(m for m in messages if m["type"] == "http.response.start")
    body = next(m for m in messages if m["type"] == "http.response.body")
    header_names = {k.lower() for k, _ in start["headers"]}

    assert body["body"] == b""
    assert b"content-length" not in header_names
    assert b"content-type" not in header_names


@pytest.mark.asyncio
async def test_cors_middleware_handles_preflight_and_simple_requests() -> None:
    async def endpoint(scope, receive, send):
        del scope, receive
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [(b"content-type", b"text/plain")],
            }
        )
        await send({"type": "http.response.body", "body": b"ok", "more_body": False})

    app = CORSMiddleware(endpoint, allow_origin="https://client.test")

    preflight = await _run_asgi(
        app,
        {
            "type": "http",
            "method": "OPTIONS",
            "path": "/",
            "query_string": b"",
            "headers": [
                (b"origin", b"https://client.test"),
                (b"access-control-request-method", b"GET"),
                (b"access-control-request-headers", b"x-custom"),
            ],
        },
    )
    preflight_start = next(m for m in preflight if m["type"] == "http.response.start")
    preflight_headers = {
        k.decode("latin-1"): v.decode("latin-1") for k, v in preflight_start["headers"]
    }
    assert preflight_start["status"] == 204
    assert preflight_headers["access-control-allow-origin"] == "https://client.test"
    assert preflight_headers["access-control-allow-headers"] == "x-custom"

    simple = await _run_asgi(
        app,
        {
            "type": "http",
            "method": "GET",
            "path": "/",
            "query_string": b"",
            "headers": [(b"origin", b"https://client.test")],
        },
    )
    simple_start = next(m for m in simple if m["type"] == "http.response.start")
    simple_headers = {
        k.decode("latin-1"): v.decode("latin-1") for k, v in simple_start["headers"]
    }
    assert simple_start["status"] == 200
    assert simple_headers["access-control-allow-origin"] == "https://client.test"


def test_cors_middleware_wsgi_preserves_duplicate_headers() -> None:
    captured: dict[str, object] = {}

    def wsgi_app(environ, start_response):
        del environ
        start_response(
            "200 OK",
            [("set-cookie", "session=abc"), ("set-cookie", "theme=dark")],
        )
        return [b"ok"]

    app = CORSMiddleware(wsgi_app, allow_origin="https://client.test")

    def start_response(status: str, headers: list[tuple[str, str]], *args):
        del args
        captured["status"] = status
        captured["headers"] = headers

    body = app.wsgi(
        {
            "REQUEST_METHOD": "GET",
            "HTTP_ORIGIN": "https://client.test",
        },
        start_response,
    )

    assert body == [b"ok"]
    assert captured["status"] == "200 OK"
    headers = captured["headers"]
    assert isinstance(headers, list)
    assert [value for key, value in headers if key.lower() == "set-cookie"] == [
        "session=abc",
        "theme=dark",
    ]
    assert (
        dict((key.lower(), value) for key, value in headers)[
            "access-control-allow-origin"
        ]
        == "https://client.test"
    )


@pytest.mark.asyncio
async def test_cors_middleware_accepts_list_origins_and_regex() -> None:
    async def endpoint(scope, receive, send):
        del scope, receive
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [],
            }
        )
        await send({"type": "http.response.body", "body": b"ok", "more_body": False})

    app = CORSMiddleware(
        endpoint,
        allow_origins=["https://allowed.example", "https://other.example"],
        allow_origin_regex=r"https://.*\.trusted\.example",
        allow_methods=["GET", "POST"],
        allow_headers=["x-custom", "authorization"],
    )

    allowed = await _run_asgi(
        app,
        {
            "type": "http",
            "method": "GET",
            "path": "/",
            "query_string": b"",
            "headers": [(b"origin", b"https://allowed.example")],
        },
    )
    allowed_headers = {
        k.decode("latin-1"): v.decode("latin-1")
        for k, v in next(m for m in allowed if m["type"] == "http.response.start")[
            "headers"
        ]
    }
    assert allowed_headers["access-control-allow-origin"] == "https://allowed.example"
    assert allowed_headers["access-control-allow-methods"] == "GET,POST"
    assert allowed_headers["access-control-allow-headers"] == "x-custom,authorization"

    regex_allowed = await _run_asgi(
        app,
        {
            "type": "http",
            "method": "GET",
            "path": "/",
            "query_string": b"",
            "headers": [(b"origin", b"https://api.trusted.example")],
        },
    )
    regex_headers = {
        k.decode("latin-1"): v.decode("latin-1")
        for k, v in next(
            m for m in regex_allowed if m["type"] == "http.response.start"
        )["headers"]
    }
    assert regex_headers["access-control-allow-origin"] == "https://api.trusted.example"
