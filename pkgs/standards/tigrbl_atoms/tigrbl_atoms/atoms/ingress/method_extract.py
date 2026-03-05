from __future__ import annotations

from typing import Any, MutableMapping

from ... import events as _ev

ANCHOR = _ev.INGRESS_METHOD_EXTRACT


def _ensure_temp(ctx: Any) -> MutableMapping[str, Any]:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    return temp


def run(obj: object | None, ctx: Any) -> None:
    del obj
    method = None

    request = getattr(ctx, "request", None)
    if request is not None:
        method = getattr(request, "method", None)

    if method is None:
        gw_raw = getattr(ctx, "gw_raw", None)
        method = getattr(gw_raw, "method", None) if gw_raw is not None else None

    if method is None:
        raw = getattr(ctx, "raw", None)
        scope = getattr(raw, "scope", None) if raw is not None else None
        if isinstance(scope, dict):
            method = scope.get("method")

    if method is None:
        return

    value = str(method).upper()
    temp = _ensure_temp(ctx)
    temp.setdefault("ingress", {})["method"] = value
    setattr(ctx, "method", value)


__all__ = ["ANCHOR", "run"]
