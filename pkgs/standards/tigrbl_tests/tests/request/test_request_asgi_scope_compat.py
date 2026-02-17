from __future__ import annotations

from tigrbl.requests import Request


def test_request_accepts_scope_with_receive_kwarg_for_compatibility() -> None:
    scope = {
        "type": "http",
        "method": "post",
        "path": "/rpc",
        "root_path": "/api",
        "headers": [(b"authorization", b"Bearer test-token")],
        "query_string": b"a=1&a=2&b=3",
        "path_params": {"tenant_id": "abc"},
        "client": ("198.51.100.77", 443),
    }

    async def _receive() -> dict[str, object]:
        return {"type": "http.request", "body": b"", "more_body": False}

    request = Request(scope, receive=_receive)

    assert request.method == "POST"
    assert request.path == "/rpc"
    assert str(request.url) == "/api/rpc?a=1&a=2&b=3"
    assert request.query == {"a": ["1", "2"], "b": ["3"]}
    assert request.path_params == {"tenant_id": "abc"}
    assert request.headers.authorization == "Bearer test-token"
    assert request.headers.get("Authorization") == "Bearer test-token"
    assert request.headers.get("authorization") == "Bearer test-token"
    assert request.bearer_token == "test-token"
    assert request.client.ip == "198.51.100.77"


def test_request_rejects_duplicated_scope_inputs() -> None:
    scope = {"type": "http", "method": "GET", "path": "/"}

    try:
        Request(scope, scope=scope)
    except TypeError as exc:
        assert "scope cannot be provided" in str(exc)
    else:  # pragma: no cover - explicit failure branch
        raise AssertionError("expected Request to reject duplicate scope inputs")
