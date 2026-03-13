from __future__ import annotations

import re

import pytest
from types import SimpleNamespace

from tigrbl_atoms.atoms.route import jsonrpc_batch_intercept, op_resolve


def _ctx_for_route(*, method: str, path: str, routes: list[object]):
    request = SimpleNamespace(method=method, path=path, url=SimpleNamespace(path=path))
    return SimpleNamespace(
        temp={"route": {}},
        request=request,
        app=SimpleNamespace(routes=routes),
    )


def test_op_resolve_marks_method_not_allowed_for_runtime_route() -> None:
    route = SimpleNamespace(
        pattern=re.compile(r"^/items/(?P<item_id>[^/]+)$"),
        methods={"GET"},
        handler=lambda: {"ok": True},
    )
    ctx = _ctx_for_route(method="POST", path="/items/abc", routes=[route])

    op_resolve._run(None, ctx)

    route_ns = ctx.temp["route"]
    assert route_ns.get("handler") is None
    assert route_ns["method_not_allowed"] is True


def test_op_resolve_finds_opmeta_index_from_proto_and_selector() -> None:
    ctx = SimpleNamespace(
        temp={"route": {}},
        proto="http.jsonrpc",
        selector="Widget.create",
        kernel_plan=SimpleNamespace(
            opmeta=[SimpleNamespace(alias="create", model=object, target="create")],
            opkey_to_meta={},
        ),
    )

    # SimpleNamespace is unhashable; use tiny hashable opkey object.
    class _OpKey:
        def __init__(self, proto: str, selector: str) -> None:
            self.proto = proto
            self.selector = selector

        def __hash__(self) -> int:
            return hash((self.proto, self.selector))

        def __eq__(self, other: object) -> bool:
            return (
                isinstance(other, _OpKey)
                and other.proto == self.proto
                and other.selector == self.selector
            )

    ctx.kernel_plan.opkey_to_meta = {_OpKey("http.jsonrpc", "Widget.create"): 0}

    op_resolve._run(None, ctx)

    assert ctx.temp["route"]["opmeta_index"] == 0


@pytest.mark.asyncio
async def test_jsonrpc_batch_intercept_short_circuits_response() -> None:
    class _App:
        jsonrpc_prefix = "/rpc"

        async def rpc_call(self, model: str, op: str, params: dict, **_: object):
            return {"model": model, "op": op, "params": params}

    payload = [
        {"jsonrpc": "2.0", "method": "Widget.create", "params": {"name": "x"}, "id": 1}
    ]
    ctx = SimpleNamespace(
        payload=payload,
        app=_App(),
        raw=SimpleNamespace(scope={"path": "/rpc"}),
        temp={"route": {}},
    )

    await jsonrpc_batch_intercept._run(None, ctx)

    route = ctx.temp["route"]
    response = ctx.temp["egress"]["transport_response"]
    assert route["short_circuit"] is True
    assert response["status_code"] == 200
    assert response["body"][0]["result"]["op"] == "create"
