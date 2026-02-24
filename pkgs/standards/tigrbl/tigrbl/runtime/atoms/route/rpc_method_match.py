from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.ROUTE_RPC_METHOD_MATCH


def run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    route = temp.setdefault("route", {})
    envelope = route.get("rpc_envelope")
    if isinstance(envelope, dict) and "method" in envelope:
        route["rpc_method"] = envelope["method"]
        proto = route.get("protocol")
        if isinstance(proto, str) and proto.endswith(".rest"):
            route["protocol"] = proto.replace(".rest", ".jsonrpc")
            setattr(ctx, "proto", route["protocol"])
