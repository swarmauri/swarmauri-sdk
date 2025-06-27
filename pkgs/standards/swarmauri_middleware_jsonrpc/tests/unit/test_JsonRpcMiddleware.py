import pytest
from fastapi import Request, Response
from swarmauri_middleware_jsonrpc.JsonRpcMiddleware import JsonRpcMiddleware


@pytest.mark.unit
@pytest.mark.asyncio
async def test_valid_jsonrpc_request():
    middleware = JsonRpcMiddleware()
    scope = {
        "type": "http",
        "method": "POST",
        "headers": [(b"content-type", b"application/json")],
    }

    async def receive():
        return {
            "type": "http.request",
            "body": b'{"jsonrpc": "2.0", "id": 1}',
            "more_body": False,
        }

    request = Request(scope=scope, receive=receive)

    async def call_next(req: Request):
        return Response("ok")

    response = await middleware.dispatch(request, call_next)
    assert isinstance(response, Response)
    assert response.status_code == 200


@pytest.mark.unit
@pytest.mark.asyncio
async def test_invalid_json():
    middleware = JsonRpcMiddleware()
    scope = {
        "type": "http",
        "method": "POST",
        "headers": [(b"content-type", b"application/json")],
    }

    async def receive():
        return {"type": "http.request", "body": b"{invalid", "more_body": False}

    request = Request(scope=scope, receive=receive)

    async def call_next(req: Request):
        return Response("ok")

    response = await middleware.dispatch(request, call_next)
    assert response.status_code == 400


@pytest.mark.unit
@pytest.mark.asyncio
async def test_missing_jsonrpc_field():
    middleware = JsonRpcMiddleware()
    scope = {
        "type": "http",
        "method": "POST",
        "headers": [(b"content-type", b"application/json")],
    }

    async def receive():
        return {"type": "http.request", "body": b"{}", "more_body": False}

    request = Request(scope=scope, receive=receive)

    async def call_next(req: Request):
        return Response("ok")

    response = await middleware.dispatch(request, call_next)
    assert response.status_code == 400
