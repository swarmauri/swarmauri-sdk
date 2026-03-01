from __future__ import annotations

from typing import Any, MutableMapping

from ... import events as _ev

ANCHOR = _ev.INGRESS_CTX_ATTACH_COMPILED


def _ensure_temp(ctx: Any) -> MutableMapping[str, Any]:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    return temp


def run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = _ensure_temp(ctx)
    ingress = temp.setdefault("ingress", {})

    compiled = getattr(ctx, "compiled", None)
    if compiled is None:
        plan = getattr(ctx, "kernel_plan", None) or getattr(ctx, "plan", None)
        compiled = getattr(plan, "compiled", None)

    if compiled is not None:
        ingress["compiled"] = compiled


__all__ = ["ANCHOR", "run"]
