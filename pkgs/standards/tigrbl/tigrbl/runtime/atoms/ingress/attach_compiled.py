from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.INGRESS_CTX_ATTACH_COMPILED


def run(obj: object | None, ctx: Any) -> None:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    compiled = getattr(ctx, "compiled", None)
    if compiled is not None:
        temp.setdefault("ingress", {})["compiled"] = compiled


__all__ = ["ANCHOR", "run"]
