from __future__ import annotations

import pytest

from tigrbl._concrete._middleware import Middleware as BaseHTTPMiddleware
from tigrbl import Request
from tigrbl import Response


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
    async def asgi(self, scope, receive, send):
        request = Request.from_scope(scope, receive)
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

        async def rewritten_receive():
            return {"type": "http.request", "body": rewritten.body, "more_body": False}

        forwarded_scope = dict(scope)
        forwarded_scope["method"] = rewritten.method
        forwarded_scope["path"] = rewritten.path
        forwarded_scope["query_string"] = b"changed=1"
        forwarded_scope["headers"] = [
            (k.encode(), v.encode()) for k, v in rewritten.headers.items()
        ]
        await self.app(forwarded_scope, rewritten_receive, send)


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
    async def asgi(self, scope, receive, send):
        del receive
        resp = Response.text("should-be-stripped", status_code=204)
        await resp(
            scope,
            lambda: {"type": "http.request", "body": b"", "more_body": False},
            send,
        )
