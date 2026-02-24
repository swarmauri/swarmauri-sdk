from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.INGRESS_HEADERS_PARSE


def run(obj: object | None, ctx: Any) -> None:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    request = getattr(ctx, "request", None)
    headers = getattr(request, "headers", None) if request is not None else None
    if headers is not None:
        temp.setdefault("ingress", {})["headers"] = dict(headers)


__all__ = ["ANCHOR", "run"]
