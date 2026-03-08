from __future__ import annotations

import json
from types import SimpleNamespace

from tigrbl_atoms.atoms.route import (
    match_fallback,
    match_jsonrpc,
    match_rest,
    match_ws,
    plan_select,
    protocol_detect,
    rpc_envelope_parse,
)


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


def test_protocol_detect_read_only_http_forces_rest() -> None:
    ctx = SimpleNamespace(
        method="GET",
        body={"jsonrpc": "2.0", "method": "Widget.read"},
        raw=SimpleNamespace(scope={"type": "http", "scheme": "http"}),
    )

    protocol_detect._run(None, ctx)

    assert ctx.temp["route"]["protocol_candidates"] == ["http.rest"]


def test_protocol_detect_ws_defaults_to_ws_scheme() -> None:
    ctx = SimpleNamespace(raw=SimpleNamespace(scope={"type": "websocket"}))

    protocol_detect._run(None, ctx)

    route = ctx.temp["route"]
    assert route["protocol_candidates"] == ["ws"]
    assert route["route_kind"] == "duplex"


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


def test_rpc_envelope_parse_reads_gw_raw_body_io_fallback() -> None:
    payload = {"jsonrpc": "2.0", "method": "Widget.update", "id": 9}
    ctx = SimpleNamespace(
        body=None,
        gw_raw=SimpleNamespace(body=json.dumps(payload).encode("utf-8")),
        temp={"route": {}},
    )

    rpc_envelope_parse._run(None, ctx)

    assert ctx.temp["route"]["rpc"]["method"] == "Widget.update"


def test_match_jsonrpc_binds_operation_from_bytes_io() -> None:
    payload = {"jsonrpc": "2.0", "method": "Widget.create", "params": {"name": "x"}}
    ctx = SimpleNamespace(
        body=json.dumps(payload).encode("utf-8"),
        temp={"route": {"protocol_candidates": ["http.jsonrpc", "http.rest"]}},
        kernel_plan=SimpleNamespace(
            proto_indices={"http.jsonrpc": {"Widget.create": 3}}
        ),
    )

    match_jsonrpc._run(None, ctx)

    route = ctx.temp["route"]
    assert route["matched"] is True
    assert route["binding"] == 3
    assert route["protocol"] == "http.jsonrpc"
    assert ctx.binding == 3


def test_match_jsonrpc_uses_route_data_when_proto_indices_missing() -> None:
    ctx = SimpleNamespace(
        body={"jsonrpc": "2.0", "method": "Widget.delete"},
        temp={"route": {"protocol_candidates": ["https.jsonrpc"]}},
        plan=SimpleNamespace(route_data={"https.jsonrpc": {"Widget.delete": 8}}),
    )

    match_jsonrpc._run(None, ctx)

    assert ctx.temp["route"]["opmeta_index"] == 8
    assert ctx.selector == "Widget.delete"


def test_match_ws_keeps_behavior_in_sync_with_jsonrpc_match() -> None:
    ctx = SimpleNamespace(
        payload={"jsonrpc": "2.0", "method": "Widget.ping"},
        temp={"route": {"protocol_candidates": ["ws.jsonrpc"]}},
        kernel_plan=SimpleNamespace(proto_indices={"ws.jsonrpc": {"Widget.ping": 4}}),
    )

    match_ws._run(None, ctx)

    assert ctx.temp["route"]["binding"] == 4
    assert ctx.protocol == "ws.jsonrpc"


def test_match_fallback_populates_defaults_without_overwriting_existing_values() -> (
    None
):
    ctx = SimpleNamespace(
        temp={"route": {"selector": "Widget.create", "path_params": {"id": "1"}}}
    )

    match_fallback._run(None, ctx)

    route = ctx.temp["route"]
    assert route["binding"] is None
    assert route["opmeta_index"] is None
    assert route["selector"] == "Widget.create"
    assert route["path_params"] == {"id": "1"}


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


def test_plan_select_keeps_existing_plan_when_no_chain_match() -> None:
    current_plan = SimpleNamespace(name="current")
    ctx = SimpleNamespace(
        temp={"route": {"opmeta_index": 1}},
        kernel_plan=SimpleNamespace(phase_chains={}),
        plan=current_plan,
    )

    plan_select._run(None, ctx)

    assert ctx.temp["route"]["plan"] is current_plan


def test_match_rest_currently_exposes_protocol_detect_behavior() -> None:
    ctx = SimpleNamespace(
        method="POST",
        body={"jsonrpc": "2.0", "method": "Widget.create"},
        raw=SimpleNamespace(scope={"type": "http", "scheme": "http"}),
    )

    match_rest._run(None, ctx)

    assert ctx.temp["route"]["protocol"] == "http.jsonrpc"
