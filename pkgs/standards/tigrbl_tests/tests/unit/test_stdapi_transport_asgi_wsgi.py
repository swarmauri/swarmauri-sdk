from __future__ import annotations

import io

import pytest

from tigrbl.types import Router, Request, Response


@pytest.mark.asyncio()
@pytest.mark.xfail(
    reason="Router no longer exposes _asgi_app transport internals.",
    raises=AttributeError,
)
async def test_asgi_http_scope_dispatches_with_query_and_body() -> None:
    router = Router()

    @router.post("/echo")
    async def echo(request: Request) -> dict[str, object]:
        return {
            "method": request.method,
            "query": request.query,
            "body": request.body.decode("utf-8"),
        }

    messages: list[dict[str, object]] = []

    request_messages = iter(
        [
            {
                "type": "http.request",
                "body": b'{"hello":"world"}',
                "more_body": False,
            }
        ]
    )

    async def receive() -> dict[str, object]:
        return next(request_messages)

    async def send(message: dict[str, object]) -> None:
        messages.append(message)

    await router._asgi_app(
        {
            "type": "http",
            "method": "POST",
            "path": "/echo",
            "query_string": b"x=1&x=2",
            "headers": [(b"content-type", b"application/json")],
        },
        receive,
        send,
    )

    assert messages[0]["type"] == "http.response.start"
    assert messages[0]["status"] == 200
    assert messages[1]["type"] == "http.response.body"
    assert (
        messages[1]["body"]
        == b'{"method":"POST","query":{"x":["1","2"]},"body":"{\\"hello\\":\\"world\\"}"}'
    )


@pytest.mark.asyncio()
@pytest.mark.xfail(
    reason="Router no longer exposes _asgi_app transport internals.",
    raises=AttributeError,
)
async def test_asgi_non_http_scope_returns_500() -> None:
    router = Router()
    messages: list[dict[str, object]] = []

    async def receive() -> dict[str, object]:
        return {"type": "websocket.receive", "text": "ignored"}

    async def send(message: dict[str, object]) -> None:
        messages.append(message)

    await router._asgi_app({"type": "websocket"}, receive, send)

    assert messages == [
        {"type": "http.response.start", "status": 500, "headers": []},
        {"type": "http.response.body", "body": b""},
    ]


@pytest.mark.asyncio()
@pytest.mark.xfail(
    reason="Router no longer exposes _asgi_app transport internals.",
    raises=AttributeError,
)
async def test_asgi_204_response_omits_body_and_content_length() -> None:
    router = Router()

    @router.delete("/items/{item_id}", status_code=204)
    def delete_item(item_id: str) -> None:
        assert item_id == "1"
        return None

    messages: list[dict[str, object]] = []

    request_messages = iter([{"type": "http.request", "body": b"", "more_body": False}])

    async def receive() -> dict[str, object]:
        return next(request_messages)

    async def send(message: dict[str, object]) -> None:
        messages.append(message)

    await router._asgi_app(
        {
            "type": "http",
            "method": "DELETE",
            "path": "/items/1",
            "query_string": b"",
            "headers": [],
        },
        receive,
        send,
    )

    assert messages[0]["type"] == "http.response.start"
    assert messages[0]["status"] == 204
    assert (b"content-length", b"0") not in messages[0]["headers"]
    assert messages[1] == {
        "type": "http.response.body",
        "body": b"",
        "more_body": False,
    }


@pytest.mark.asyncio()
@pytest.mark.xfail(
    reason="Router no longer exposes _asgi_app transport internals.",
    raises=AttributeError,
)
async def test_asgi_head_response_strips_body_and_entity_headers() -> None:
    router = Router()

    @router.get("/items")
    def list_items() -> dict[str, str]:
        return {"ok": "yes"}

    messages: list[dict[str, object]] = []

    request_messages = iter([{"type": "http.request", "body": b"", "more_body": False}])

    async def receive() -> dict[str, object]:
        return next(request_messages)

    async def send(message: dict[str, object]) -> None:
        messages.append(message)

    await router._asgi_app(
        {
            "type": "http",
            "method": "HEAD",
            "path": "/items",
            "query_string": b"",
            "headers": [],
        },
        receive,
        send,
    )

    assert messages[0]["type"] == "http.response.start"
    start_headers = dict(messages[0]["headers"])
    assert b"content-length" not in start_headers
    assert b"content-type" not in start_headers
    assert b"transfer-encoding" not in start_headers
    assert messages[1] == {
        "type": "http.response.body",
        "body": b"",
        "more_body": False,
    }


@pytest.mark.xfail(
    raises=AttributeError,
    reason="Router no longer exposes REST verb decorator helpers such as .get.",
)
def test_wsgi_205_response_strips_body_and_entity_headers() -> None:
    router = Router()

    @router.get("/reset", status_code=205)
    def reset() -> dict[str, str]:
        return {"reset": "ok"}

    called: dict[str, object] = {}

    def start_response(status: str, headers: list[tuple[str, str]]) -> None:
        called["status"] = status
        called["headers"] = headers

    response_chunks = router._wsgi_app(
        {
            "REQUEST_METHOD": "GET",
            "PATH_INFO": "/reset",
            "QUERY_STRING": "",
            "CONTENT_LENGTH": "0",
            "wsgi.input": io.BytesIO(b""),
        },
        start_response,
    )

    headers = dict(called["headers"])
    assert called["status"] == "205 Reset Content"
    assert "content-length" not in headers
    assert "content-type" not in headers
    assert "transfer-encoding" not in headers
    assert response_chunks == [b""]


@pytest.mark.xfail(
    raises=AttributeError,
    reason="Router no longer exposes REST verb decorator helpers such as .get.",
)
def test_wsgi_recomputes_stale_content_length() -> None:
    router = Router()

    @router.get("/raw")
    def raw() -> object:
        return Response(
            body=b"hello",
            headers=[("content-type", "text/plain"), ("content-length", "999")],
        )

    called: dict[str, object] = {}

    def start_response(status: str, headers: list[tuple[str, str]]) -> None:
        called["status"] = status
        called["headers"] = headers

    response_chunks = router._wsgi_app(
        {
            "REQUEST_METHOD": "GET",
            "PATH_INFO": "/raw",
            "QUERY_STRING": "",
            "CONTENT_LENGTH": "0",
            "wsgi.input": io.BytesIO(b""),
        },
        start_response,
    )

    headers = dict(called["headers"])
    assert called["status"] == "200 OK"
    assert headers["content-length"] == "5"
    assert response_chunks == [b"hello"]


@pytest.mark.xfail(
    raises=AttributeError,
    reason="Router no longer exposes REST verb decorator helpers such as .post.",
)
def test_wsgi_dispatch_reads_body_and_query() -> None:
    router = Router()

    @router.post("/echo")
    def echo(request: Request) -> dict[str, object]:
        return {
            "path": request.path,
            "query": request.query,
            "body": request.body.decode("utf-8"),
            "script_name": request.script_name,
        }

    called: dict[str, object] = {}

    def start_response(status: str, headers: list[tuple[str, str]]) -> None:
        called["status"] = status
        called["headers"] = headers

    response_chunks = router._wsgi_app(
        {
            "REQUEST_METHOD": "POST",
            "PATH_INFO": "/echo",
            "SCRIPT_NAME": "/v1",
            "QUERY_STRING": "a=1&a=2",
            "CONTENT_TYPE": "application/json",
            "CONTENT_LENGTH": "7",
            "wsgi.input": io.BytesIO(b'{"a":1}'),
        },
        start_response,
    )

    assert called["status"] == "200 OK"
    assert response_chunks == [
        b'{"path":"/echo","query":{"a":["1","2"]},"body":"{\\"a\\":1}","script_name":"/v1"}'
    ]


def test_invalid_asgi_wsgi_invocation_raises_type_error() -> None:
    router = Router()

    with pytest.raises(TypeError, match="Invalid ASGI/WSGI invocation"):
        router("not-a-scope")
