from __future__ import annotations

import json
from types import SimpleNamespace

from tigrbl_atoms.atoms.route import (
    REGISTRY,
    ctx_finalize,
    match_fallback,
    match_jsonrpc,
    match_rest,
    match_ws,
    op_resolve,
    plan_select,
    program_resolve,
    protocol_detect,
    rpc_envelope_parse,
    selector_resolve,
)
from tigrbl_atoms.types import Atom


def test_route_registry_contains_expected_atoms() -> None:
    assert set(REGISTRY) == {
        ("route", "protocol_detect"),
        ("route", "rpc_envelope_parse"),
        ("route", "match_jsonrpc"),
        ("route", "match_rest"),
        ("route", "match_ws"),
        ("route", "match_fallback"),
        ("route", "selector_resolve"),
        ("route", "program_resolve"),
        ("route", "params_normalize"),
        ("route", "payload_select"),
        ("route", "op_resolve"),
        ("route", "plan_select"),
        ("route", "ctx_finalize"),
        ("route", "jsonrpc_batch_intercept"),
    }


def test_route_instances_and_impls_use_atom_contract() -> None:
    modules = (
        protocol_detect,
        rpc_envelope_parse,
        match_jsonrpc,
        match_rest,
        match_ws,
        match_fallback,
        selector_resolve,
        program_resolve,
        op_resolve,
        plan_select,
        ctx_finalize,
    )
    for module in modules:
        assert isinstance(module.INSTANCE, Atom)
        assert issubclass(module.AtomImpl, Atom)
        assert module.INSTANCE.anchor == module.ANCHOR


def test_protocol_detect_http_jsonrpc_candidate_order() -> None:
    ctx = SimpleNamespace(
        method="POST",
        body={"jsonrpc": "2.0", "method": "Widget.create"},
        raw=SimpleNamespace(scope={"type": "http", "scheme": "https"}),
    )

    protocol_detect._run(None, ctx)

    route = ctx.temp["route"]
    assert route["protocol_candidates"] == ["https.jsonrpc", "https.rest"]
    assert route["protocol"] == "https.jsonrpc"
    assert route["route_kind"] == "request_response"
    assert ctx.protocol == "https.jsonrpc"


def test_rpc_envelope_parse_reads_body_bytes_io() -> None:
    payload = {
        "jsonrpc": "2.0",
        "method": "Widget.create",
        "params": {"name": "x"},
        "id": 7,
    }
    ctx = SimpleNamespace(body=json.dumps(payload).encode("utf-8"), temp={"route": {}})

    rpc_envelope_parse._run(None, ctx)

    assert ctx.temp["route"]["rpc"]["method"] == "Widget.create"
    assert ctx.temp["route"]["rpc"]["params"] == {"name": "x"}
    assert ctx.temp["route"]["rpc_method"] == "Widget.create"


def test_match_atoms_collect_protocol_candidates() -> None:
    ctx = SimpleNamespace(
        temp={
            "route": {
                "protocol_candidates": ["http.jsonrpc", "http.rest", "ws.jsonrpc"]
            }
        }
    )

    match_jsonrpc._run(None, ctx)
    match_rest._run(None, ctx)
    match_ws._run(None, ctx)

    route = ctx.temp["route"]
    assert route["jsonrpc_candidates"] == ["http.jsonrpc", "ws.jsonrpc"]
    assert route["rest_candidates"] == ["http.rest"]
    assert route["ws_candidates"] == ["ws.jsonrpc"]


def test_match_fallback_populates_defaults() -> None:
    ctx = SimpleNamespace(temp={"route": {"selector": "Widget.create"}})

    match_fallback._run(None, ctx)

    route = ctx.temp["route"]
    assert route["matched"] is False
    assert route["selector"] == "Widget.create"
    assert route["path_params"] == {}


def test_selector_resolve_matches_jsonrpc_operation() -> None:
    packed = SimpleNamespace(
        selector_to_id={"Widget.create": 11},
        proto_to_id={"http.jsonrpc": 7},
    )
    ctx = SimpleNamespace(
        body={"jsonrpc": "2.0", "method": "Widget.create"},
        temp={"route": {"protocol_candidates": ["http.jsonrpc"]}},
        kernel_plan=SimpleNamespace(
            proto_indices={"http.jsonrpc": {"Widget.create": 3}},
            packed=packed,
        ),
    )

    selector_resolve._run(None, ctx)

    route = ctx.temp["route"]
    assert route["matched"] is True
    assert route["protocol"] == "http.jsonrpc"
    assert route["selector"] == "Widget.create"
    assert route["proto_id"] == 7
    assert route["selector_id"] == 11
    assert ctx.protocol == "http.jsonrpc"
    assert ctx.selector == "Widget.create"


def test_program_resolve_maps_proto_selector_ids_to_program() -> None:
    packed = SimpleNamespace(route_to_program=[[0, 5], [2, 3]])
    ctx = SimpleNamespace(
        temp={"proto_id": 0, "selector_id": 1, "route": {}},
        kernel_plan=SimpleNamespace(packed=packed),
    )

    program_resolve._run(None, ctx)

    route = ctx.temp["route"]
    assert route["program_id"] == 5
    assert route["binding"] == 5
    assert route["opmeta_index"] == 5
    assert ctx.binding == 5


def test_op_resolve_populates_model_alias_target_and_default_status() -> None:
    meta = SimpleNamespace(model="WidgetModel", alias="create", target="widgets")
    ctx = SimpleNamespace(
        temp={"route": {"binding": 0}},
        kernel_plan=SimpleNamespace(opmeta=[meta]),
    )

    op_resolve._run(None, ctx)

    route = ctx.temp["route"]
    assert route["binding"] == 0
    assert route["program_id"] == 0
    assert route["opmeta_index"] == 0
    assert route["status_code"] == 201
    assert ctx.model == "WidgetModel"
    assert ctx.op == "create"
    assert ctx.target == "widgets"
    assert ctx.status_code == 201


def test_plan_select_uses_kernel_plan_phase_chain_when_opmeta_index_exists() -> None:
    selected = object()
    ctx = SimpleNamespace(
        temp={"route": {"opmeta_index": 5}},
        kernel_plan=SimpleNamespace(phase_chains={5: selected}),
        plan=SimpleNamespace(name="kernel-plan"),
    )

    plan_select._run(None, ctx)

    assert ctx.temp["route"]["plan"] is selected
    assert ctx.plan is selected


def test_ctx_finalize_marks_route_finalized_and_attaches_helpers() -> None:
    session = object()
    adapter = object()
    serializer = object()
    ctx = SimpleNamespace(
        temp={"route": {"opmeta_index": 1}},
        db_factory=lambda: session,
        response_adapter_factory=lambda _ctx: adapter,
        serializer_factory=lambda _ctx: serializer,
    )

    ctx_finalize._run(None, ctx)

    assert ctx.temp["route"]["finalized"] is True
    assert ctx.session is session
    assert ctx.db is session
    assert ctx.response_adapter is adapter
    assert ctx.serializer is serializer
