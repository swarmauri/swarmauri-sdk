from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.ROUTE_OP_RESOLVE


def _default_status_for_target(target: Any) -> int:
    token: Any = target
    if isinstance(token, dict):
        token = token.get("target") or token.get("alias")
    elif not isinstance(token, str):
        token = getattr(token, "target", None) or getattr(token, "alias", None)

    if isinstance(token, str):
        token = token.rsplit(".", 1)[-1].lower()

    return 201 if token in {"create", "bulk_create"} else 200


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
            setattr(ctx, "op", getattr(meta, "alias", None))
            setattr(ctx, "model", getattr(meta, "model", None))
            if getattr(ctx, "status_code", None) is None:
                setattr(
                    ctx,
                    "status_code",
                    _default_status_for_target(getattr(meta, "target", None)),
                )
            return

    if "op" not in route:
        route["op"] = getattr(ctx, "op", None)
