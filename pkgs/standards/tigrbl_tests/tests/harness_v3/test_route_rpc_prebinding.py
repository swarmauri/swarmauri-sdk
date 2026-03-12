from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from tigrbl_atoms.atoms.route import rpc_envelope_parse
from tigrbl.runtime.gw.raw import GwRouteEnvelope


def _mk_ctx(body: bytes):
    return SimpleNamespace(
        temp={"route": {"protocol": "http.rest"}},
        proto="http.rest",
        body=body,
        gw_raw=GwRouteEnvelope(
            transport="http",
            scheme="http",
            kind="maybe-jsonrpc",
            method="POST",
            path="/rpc",
            headers={"content-type": "application/json"},
            query={},
            body=None,
            ws_event=None,
            rpc=None,
        ),
    )


@pytest.mark.skip(reason="binding_match atom removed in refactor")
def test_binding_match_resolves_jsonrpc_before_envelope_parse() -> None:
    pass


def test_rpc_envelope_parse_uses_ctx_body_when_route_body_missing() -> None:
    payload = {"jsonrpc": "2.0", "method": "Gadget.create", "params": {}, "id": 1}
    ctx = _mk_ctx(json.dumps(payload).encode("utf-8"))

    rpc_envelope_parse.run(None, ctx)

    assert ctx.temp["route"]["rpc_envelope"]["method"] == "Gadget.create"
    assert ctx.gw_raw.kind == "jsonrpc"
    assert ctx.gw_raw.rpc is not None
    assert ctx.gw_raw.rpc.get("id") == 1
