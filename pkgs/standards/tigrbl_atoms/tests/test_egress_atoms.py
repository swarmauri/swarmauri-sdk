from __future__ import annotations

import asyncio
from types import SimpleNamespace

from tigrbl_atoms.atoms.egress import REGISTRY
from tigrbl_atoms.atoms.egress import (
    asgi_send,
    envelope_apply,
    headers_apply,
    http_finalize,
    out_dump,
    result_normalize,
    to_transport_response,
)
from tigrbl_atoms.types import Atom, EgressedCtx, EmittingCtx


def test_egress_registry_contains_expected_atoms() -> None:
    assert set(REGISTRY) == {
        ("egress", "result_normalize"),
        ("egress", "out_dump"),
        ("egress", "envelope_apply"),
        ("egress", "headers_apply"),
        ("egress", "http_finalize"),
        ("egress", "to_transport_response"),
        ("egress", "asgi_send"),
    }


def test_egress_registry_binds_expected_anchor_and_instance() -> None:
    assert REGISTRY[("egress", "result_normalize")] == (
        result_normalize.ANCHOR,
        result_normalize.INSTANCE,
    )
    assert REGISTRY[("egress", "out_dump")] == (out_dump.ANCHOR, out_dump.INSTANCE)
    assert REGISTRY[("egress", "envelope_apply")] == (
        envelope_apply.ANCHOR,
        envelope_apply.INSTANCE,
    )
    assert REGISTRY[("egress", "headers_apply")] == (
        headers_apply.ANCHOR,
        headers_apply.INSTANCE,
    )
    assert REGISTRY[("egress", "http_finalize")] == (
        http_finalize.ANCHOR,
        http_finalize.INSTANCE,
    )
    assert REGISTRY[("egress", "to_transport_response")] == (
        to_transport_response.ANCHOR,
        to_transport_response.INSTANCE,
    )
    assert REGISTRY[("egress", "asgi_send")] == (asgi_send.ANCHOR, asgi_send.INSTANCE)


def test_egress_instances_and_impls_use_atom_contract() -> None:
    modules = (
        result_normalize,
        out_dump,
        envelope_apply,
        headers_apply,
        http_finalize,
        to_transport_response,
        asgi_send,
    )

    for module in modules:
        assert isinstance(module.INSTANCE, Atom)
        assert issubclass(module.AtomImpl, Atom)
        assert module.INSTANCE.anchor == module.ANCHOR


def test_result_normalize_sets_result_none_when_rpc_error_is_present() -> None:
    ctx = SimpleNamespace(result={"ok": True}, temp={"rpc_error": {"code": -32600}})

    result_normalize._run(None, ctx)

    assert ctx.temp["egress"]["result"] is None
    assert ctx.result is None


def test_out_dump_prefers_response_payload_then_falls_back_to_result() -> None:
    ctx = SimpleNamespace(result={"ok": True}, temp={"response_payload": {"wire": "v"}})

    out_dump._run(None, ctx)

    assert ctx.temp["egress"]["wire_payload"] == {"wire": "v"}


def test_envelope_apply_builds_jsonrpc_envelope_with_id() -> None:
    ctx = SimpleNamespace(
        result={"ok": True},
        gw_raw=SimpleNamespace(kind="jsonrpc", rpc={"id": 9}),
        temp={"egress": {"wire_payload": {"ok": True}}},
    )

    envelope_apply._run(None, ctx)

    assert ctx.temp["egress"]["enveloped"] == {
        "jsonrpc": "2.0",
        "result": {"ok": True},
        "id": 9,
    }


def test_headers_apply_sets_json_content_type_for_mapping_body() -> None:
    ctx = SimpleNamespace(temp={"egress": {"enveloped": {"ok": True}}})

    headers_apply._run(None, ctx)

    assert ctx.temp["egress"]["headers"]["content-type"] == "application/json"


def test_http_finalize_forces_200_for_jsonrpc_requests() -> None:
    ctx = SimpleNamespace(
        status_code=418,
        gw_raw=SimpleNamespace(kind="jsonrpc"),
        temp={"egress": {"status_code": 418}},
    )

    http_finalize._run(None, ctx)

    assert ctx.temp["egress"]["status_code"] == 200
    assert ctx.status_code == 200


def test_to_transport_response_sets_transport_response_on_emitting_ctx() -> None:
    ctx = EmittingCtx()
    ctx.temp["egress"] = {
        "enveloped": {"ok": True},
        "headers": {"x-test": "1"},
        "status_code": 202,
    }

    out = asyncio.run(to_transport_response.INSTANCE(None, ctx))

    assert isinstance(out, EmittingCtx)
    assert out.transport_response == {
        "status_code": 202,
        "headers": {"x-test": "1"},
        "body": {"ok": True},
    }


def test_asgi_send_emits_http_messages_and_promotes_to_egressed_ctx() -> None:
    sent: list[dict[str, object]] = []

    async def send(message: dict[str, object]) -> None:
        sent.append(message)

    ctx = EmittingCtx()
    ctx.raw = SimpleNamespace(scope={"type": "http", "method": "GET"}, send=send)
    ctx.temp["egress"] = {
        "transport_response": {
            "status_code": 200,
            "headers": {"content-type": "application/json"},
            "body": {"ok": True},
        }
    }

    out = asyncio.run(asgi_send.INSTANCE(None, ctx))

    assert isinstance(out, EgressedCtx)
    assert len(sent) == 2
    assert sent[0]["type"] == "http.response.start"
    assert sent[1]["type"] == "http.response.body"
    assert ctx.temp["egress"]["response_sent"] is True
