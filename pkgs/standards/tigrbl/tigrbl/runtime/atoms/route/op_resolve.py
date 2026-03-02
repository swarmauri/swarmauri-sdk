from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.ROUTE_OP_RESOLVE


def run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    route = temp.setdefault("route", {})

    maybe_index = route.get("binding")
    if isinstance(maybe_index, int):
        plan = getattr(ctx, "kernel_plan", None) or getattr(ctx, "plan", None)
        opmeta = getattr(plan, "opmeta", ()) if plan is not None else ()
        if 0 <= maybe_index < len(opmeta):
            meta = opmeta[maybe_index]
            route["opmeta_index"] = maybe_index
            route["op"] = getattr(meta, "alias", None)
            route["target"] = getattr(meta, "target", None)
            setattr(ctx, "op", getattr(meta, "alias", None))
            setattr(ctx, "model", getattr(meta, "model", None))
            setattr(ctx, "op_target", getattr(meta, "target", None))
            return

    if "op" not in route:
        route["op"] = getattr(ctx, "op", None)
