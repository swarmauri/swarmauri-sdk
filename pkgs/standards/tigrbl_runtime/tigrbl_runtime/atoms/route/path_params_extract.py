from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.ROUTE_PATH_PARAMS_EXTRACT


def run(obj: object | None, ctx: Any) -> None:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    request = getattr(ctx, "request", None)
    path_params = getattr(request, "path_params", None) if request is not None else None
    if path_params:
        temp.setdefault("route", {})["path_params"] = dict(path_params)


__all__ = ["ANCHOR", "run"]
