from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.ROUTE_BINDING_MATCH


def run(obj: object | None, ctx: Any) -> None:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    route = temp.setdefault("route", {})
    if "binding" not in route:
        route["binding"] = getattr(ctx, "binding", None)


__all__ = ["ANCHOR", "run"]
