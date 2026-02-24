from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.ROUTE_BINDING_MATCH


def run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    route = temp.setdefault("route", {})

    plan = getattr(ctx, "kernel_plan", None) or getattr(ctx, "plan", None)
    proto = route.get("protocol") or getattr(ctx, "proto", None)
    if not isinstance(proto, str):
        return

    proto_indices = getattr(plan, "proto_indices", None)
    if not isinstance(proto_indices, dict):
        route.setdefault("binding", getattr(ctx, "binding", None))
        return

    index = proto_indices.get(proto)
    if not isinstance(index, dict):
        return

    selector = None
    if proto.endswith(".rest"):
        env = getattr(ctx, "gw_raw", None)
        method = getattr(env, "method", None)
        path = getattr(env, "path", None)
        if isinstance(method, str) and isinstance(path, str):
            selector = f"{method.upper()} {path}"
    elif proto.endswith(".jsonrpc"):
        selector = route.get("rpc_method")

    if isinstance(selector, str):
        route["binding"] = index.get(selector)
