from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.INGRESS_METHOD_EXTRACT


def run(obj: object | None, ctx: Any) -> None:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    request = getattr(ctx, "request", None)
    method = getattr(request, "method", None) if request is not None else None
    if method is not None:
        temp.setdefault("ingress", {})["method"] = str(method).upper()


__all__ = ["ANCHOR", "run"]
