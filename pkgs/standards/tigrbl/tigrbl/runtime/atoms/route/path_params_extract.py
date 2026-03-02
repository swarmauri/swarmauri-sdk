from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.ROUTE_PATH_PARAMS_EXTRACT


def run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    route = temp.setdefault("route", {})

    existing = route.get("path_params")
    if isinstance(existing, dict):
        setattr(ctx, "path_params", dict(existing))
        try:
            ctx["path_params"] = dict(existing)
        except Exception:
            pass
        return

    request = getattr(ctx, "request", None)
    path_params = getattr(request, "path_params", None) if request is not None else None
    if path_params is not None:
        parsed = dict(path_params)
        route["path_params"] = parsed
        setattr(ctx, "path_params", parsed)
        try:
            ctx["path_params"] = parsed
        except Exception:
            pass


__all__ = ["ANCHOR", "run"]
