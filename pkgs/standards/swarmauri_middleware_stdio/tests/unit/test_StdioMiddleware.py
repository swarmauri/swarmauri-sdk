import pytest
from fastapi import Request, Response
from swarmauri_middleware_stdio.StdioMiddleware import StdioMiddleware


@pytest.mark.unit
@pytest.mark.asyncio
async def test_dispatch_logs_and_returns_response():
    middleware = StdioMiddleware()
    scope = {"type": "http", "method": "GET", "path": "/", "headers": []}
    request = Request(scope=scope)

    async def call_next(req: Request):
        return Response("ok")

    response = await middleware.dispatch(request, call_next)
    assert isinstance(response, Response)
