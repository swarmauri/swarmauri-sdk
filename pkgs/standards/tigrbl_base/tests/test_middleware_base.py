import pytest

from tigrbl_base._base._middleware_base import (
    MiddlewareBase,
    finalize_transport_response,
)
from tigrbl_base._base._request_base import RequestBase


@pytest.mark.asyncio
async def test_middleware_dispatch_passthrough() -> None:
    middleware = MiddlewareBase(lambda *_: None)
    request = RequestBase(
        method="GET",
        path="/",
        headers={},
        query={},
        path_params={},
        body=b"",
        script_name="",
    )

    async def call_next(req: RequestBase):
        return req

    result = await middleware.dispatch(request, call_next)
    assert result is request


def test_finalize_transport_response_passthrough() -> None:
    headers = [(b"a", b"b")]
    body = b"payload"

    out_headers, out_body = finalize_transport_response({}, 200, headers, body)
    assert out_headers == headers
    assert out_body == body


def test_scope_from_request_normalizes_fields() -> None:
    request = RequestBase(
        method="POST",
        path="/items",
        headers={"x-token": "1"},
        query={"q": ["a", "b"]},
        path_params={},
        body=b"",
        script_name="/root",
    )

    scope = MiddlewareBase._scope_from_request({"type": "http"}, request)
    assert scope["method"] == "POST"
    assert scope["path"] == "/items"
    assert scope["query_string"] == b"q=a&q=b"
    assert scope["headers"] == [(b"x-token", b"1")]
    assert scope["root_path"] == "/root"
