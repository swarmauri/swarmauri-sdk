from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.ROUTE_BINDING_POLICY_APPLY


def run(obj: object | None, ctx: Any) -> None:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    route = temp.setdefault("route", {})
    if "policy" not in route:
        route["policy"] = getattr(ctx, "binding_policy", None)


__all__ = ["ANCHOR", "run"]
