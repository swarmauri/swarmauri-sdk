from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from ... import events as _ev

ANCHOR = _ev.ROUTE_OP_RESOLVE


def _default_status_for_target(target: Any) -> int:
    return 201 if target == "create" else 200


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
            op_alias = getattr(meta, "alias", None)
            route["op"] = op_alias
            setattr(ctx, "op", op_alias)
            setattr(ctx, "model", getattr(meta, "model", None))
            if getattr(ctx, "env", None) is None:
                payload = route.get("payload") if isinstance(route, dict) else None
                if payload is None:
                    payload = getattr(ctx, "payload", None)
                setattr(
                    ctx,
                    "env",
                    SimpleNamespace(
                        method=op_alias,
                        params=payload,
                        target=getattr(meta, "target", None),
                        model=getattr(meta, "model", None),
                    ),
                )
            if getattr(ctx, "status_code", None) is None:
                setattr(
                    ctx,
                    "status_code",
                    _default_status_for_target(getattr(meta, "target", None)),
                )
            return

    if "op" not in route:
        route["op"] = getattr(ctx, "op", None)
