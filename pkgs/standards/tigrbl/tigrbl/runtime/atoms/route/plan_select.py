from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.ROUTE_PLAN_SELECT


def run(obj: object | None, ctx: Any) -> None:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    plan = getattr(ctx, "plan", None)
    if plan is not None:
        temp.setdefault("route", {})["plan"] = plan


__all__ = ["ANCHOR", "run"]
