from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.INGRESS_QUERY_PARSE


def run(obj: object | None, ctx: Any) -> None:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    request = getattr(ctx, "request", None)
    query = getattr(request, "query_params", None) if request is not None else None
    if query is not None:
        temp.setdefault("ingress", {})["query"] = dict(query)


__all__ = ["ANCHOR", "run"]
