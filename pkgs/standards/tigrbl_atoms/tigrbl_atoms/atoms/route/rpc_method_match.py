from __future__ import annotations

from ...types import Atom, Ctx, RoutedCtx
from ...stages import Ingress, Routed

from typing import Any

from ... import events as _ev

ANCHOR = _ev.ROUTE_RPC_METHOD_MATCH


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    route = temp.setdefault("route", {})
    envelope = route.get("rpc_envelope")
    if isinstance(envelope, dict) and "method" in envelope:
        rpc_method = envelope["method"]
        route["rpc_method"] = rpc_method
        # JSON-RPC transport always returns HTTP 200 with an enveloped payload.
        setattr(ctx, "status_code", 200)
        proto = route.get("protocol")
        if isinstance(proto, str) and proto.endswith(".rest"):
            route["protocol"] = proto.replace(".rest", ".jsonrpc")
            setattr(ctx, "proto", route["protocol"])

        # Binding selection is performed by ``binding_match`` before RPC parsing.
        # Once the RPC method is known, resolve the selected JSON-RPC op index
        # from the compiled protocol index without re-running binding_match.
        plan = getattr(ctx, "kernel_plan", None) or getattr(ctx, "plan", None)
        proto = route.get("protocol")
        proto_indices = getattr(plan, "proto_indices", None)
        if isinstance(proto, str) and isinstance(proto_indices, dict):
            method_index = proto_indices.get(proto)
            if isinstance(method_index, dict):
                binding = method_index.get(rpc_method)
                if isinstance(binding, int):
                    route["binding"] = binding


class AtomImpl(Atom[Ingress, Routed]):
    name = "route.rpc_method_match"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Ingress]) -> Ctx[Routed]:
        _run(obj, ctx)
        return ctx.promote(RoutedCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
