import pytest

from swarmauri_middleware_tracetiming.TraceTimingMiddleware import TraceTimingMiddleware


@pytest.mark.asyncio
async def test_on_scope_creates_traceparent_when_missing() -> None:
    middleware = TraceTimingMiddleware()
    scope = {"type": "http", "headers": []}

    result_scope = await middleware.on_scope(scope)

    headers = dict(result_scope["headers"])
    assert b"traceparent" in headers
    assert result_scope["_swarmauri_traceparent"].startswith("00-")


@pytest.mark.asyncio
async def test_on_send_sets_server_timing_and_trace_headers() -> None:
    middleware = TraceTimingMiddleware(edge_ms_getter=lambda _: 15.0)
    scope = {
        "type": "http",
        "headers": [
            (b"traceparent", b"00-11111111111111111111111111111111-2222222222222222-01")
        ],
    }
    scope = await middleware.on_scope(scope)

    message = {
        "type": "http.response.start",
        "status": 200,
        "headers": [],
    }

    updated = await middleware.on_send(scope, message)
    headers = dict(updated["headers"])

    assert b"server-timing" in headers
    assert b"app;dur=" in headers[b"server-timing"]
    assert b"edge;dur=15.0" in headers[b"server-timing"]
    assert b"timing-allow-origin" in headers
    assert b"traceparent" in headers
