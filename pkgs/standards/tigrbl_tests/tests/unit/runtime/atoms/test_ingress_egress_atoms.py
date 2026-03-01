from __future__ import annotations

from types import SimpleNamespace

from tigrbl.runtime.atoms.egress import (
    envelope_apply,
    headers_apply,
    http_finalize,
    out_dump,
    result_normalize,
    to_transport_response,
)
from tigrbl.runtime.atoms.ingress import (
    attach_compiled,
    body_peek,
    body_read,
    ctx_init,
    headers_parse,
    method_extract,
    path_extract,
    query_parse,
    raw_from_scope,
)


def _ctx(**kwargs):
    base = {"temp": {}}
    base.update(kwargs)
    return SimpleNamespace(**base)


def test_ingress_atoms_extract_http_request_bits() -> None:
    raw = SimpleNamespace(
        scope={
            "type": "http",
            "scheme": "https",
            "method": "post",
            "path": "/v1/widgets",
            "query_string": b"a=1&a=2&empty=",
            "headers": [
                (b"content-type", b"application/json"),
                (b"x-test", b"one"),
                (b"x-test", b"two"),
            ],
        }
    )
    ctx = _ctx(raw=raw, body=b'{"jsonrpc":"2.0","method":"Widget.create"}')

    ctx_init.run(None, ctx)
    attach_compiled.run(None, ctx)
    raw_from_scope.run(None, ctx)
    method_extract.run(None, ctx)
    path_extract.run(None, ctx)
    headers_parse.run(None, ctx)
    query_parse.run(None, ctx)

    assert ctx.temp["ingress"]["ctx_initialized"] is True
    assert ctx.temp["ingress"]["method"] == "POST"
    assert ctx.temp["ingress"]["path"] == "/v1/widgets"
    assert ctx.temp["ingress"]["headers"]["x-test"] == ["one", "two"]
    assert ctx.temp["ingress"]["query"] == {"a": ["1", "2"], "empty": [""]}
    assert ctx.gw_raw.transport == "http"
    assert ctx.gw_raw.scheme == "https"
    assert ctx.gw_raw.kind == "maybe-jsonrpc"


def test_ingress_body_read_and_peek_capture_asgi_payload() -> None:
    messages = iter(
        [
            {"type": "http.request", "body": b"abc", "more_body": True},
            {"type": "http.request", "body": b"def", "more_body": False},
        ]
    )

    async def receive():
        return next(messages)

    ctx = _ctx(raw=SimpleNamespace(scope={"type": "http"}, receive=receive))

    import asyncio

    asyncio.run(body_read.run(None, ctx))
    body_peek.run(None, ctx)

    assert ctx.temp["ingress"]["body"] == b"abcdef"
    assert ctx.temp["ingress"]["body_peek"] == b"abcdef"
    assert ctx.body_bytes == b"abcdef"


def test_egress_atoms_build_transport_response() -> None:
    ctx = _ctx(result={"ok": True}, response_headers={"x-id": "123"}, status_code=201)

    result_normalize.run(None, ctx)
    out_dump.run(None, ctx)
    envelope_apply.run(None, ctx)
    headers_apply.run(None, ctx)
    http_finalize.run(None, ctx)
    to_transport_response.run(None, ctx)

    egress = ctx.temp["egress"]
    assert egress["result"] == {"ok": True}
    assert egress["wire_payload"] == {"ok": True}
    assert egress["enveloped"] == {"data": {"ok": True}}
    assert egress["headers"] == {"x-id": "123"}
    assert egress["status_code"] == 201
    assert egress["transport_response"] == {
        "status_code": 201,
        "headers": {"x-id": "123"},
        "body": {"data": {"ok": True}},
    }


def test_raw_from_scope_flags_jsonrpc_and_rest_kinds() -> None:
    rpc_ctx = _ctx(
        raw=SimpleNamespace(
            scope={
                "type": "http",
                "method": "POST",
                "path": "/rpc",
                "query_string": b"",
                "headers": [(b"content-type", b"application/json")],
            }
        )
    )
    raw_from_scope.run(None, rpc_ctx)
    assert rpc_ctx.gw_raw.kind == "maybe-jsonrpc"

    rest_ctx = _ctx(
        raw=SimpleNamespace(
            scope={
                "type": "http",
                "method": "GET",
                "path": "/items",
                "query_string": b"",
                "headers": [(b"content-type", b"text/plain")],
            }
        )
    )
    raw_from_scope.run(None, rest_ctx)
    assert rest_ctx.gw_raw.kind == "rest"

    ws_ctx = _ctx(
        raw=SimpleNamespace(
            scope={
                "type": "websocket",
                "scheme": "wss",
                "path": "/ws",
                "query_string": b"token=abc",
                "headers": [(b"host", b"example.org")],
            }
        ),
        raw_event={"type": "websocket.connect"},
    )
    raw_from_scope.run(None, ws_ctx)
    assert ws_ctx.gw_raw.transport == "ws"
    assert ws_ctx.gw_raw.ws_event == {"type": "websocket.connect"}
