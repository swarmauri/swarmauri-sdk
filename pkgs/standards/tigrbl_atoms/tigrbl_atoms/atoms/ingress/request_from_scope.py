from __future__ import annotations

from typing import Any, MutableMapping

from ... import events as _ev
from tigrbl_concrete._concrete._request import Request

ANCHOR = _ev.INGRESS_REQUEST_FROM_SCOPE


def _ensure_temp(ctx: Any) -> MutableMapping[str, Any]:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    return temp


def run(obj: object | None, ctx: Any) -> None:
    del obj
    raw = getattr(ctx, "raw", None)
    scope = getattr(raw, "scope", None) if raw is not None else None
    if not isinstance(scope, dict):
        return

    req = Request(scope, app=getattr(ctx, "app", None))
    setattr(ctx, "request", req)

    temp = _ensure_temp(ctx)
    temp.setdefault("ingress", {})["request"] = req


__all__ = ["ANCHOR", "run"]
