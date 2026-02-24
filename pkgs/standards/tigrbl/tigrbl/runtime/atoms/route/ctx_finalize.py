from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.ROUTE_CTX_FINALIZE


def run(obj: object | None, ctx: Any) -> None:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    temp.setdefault("route", {})["finalized"] = True


__all__ = ["ANCHOR", "run"]
