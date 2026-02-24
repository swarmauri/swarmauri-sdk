from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.INGRESS_PATH_EXTRACT


def run(obj: object | None, ctx: Any) -> None:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    request = getattr(ctx, "request", None)
    url = getattr(request, "url", None) if request is not None else None
    value = (
        getattr(url, "path", None)
        if url is not None
        else getattr(request, "path", None)
        if request is not None
        else None
    )
    if value is not None:
        temp.setdefault("ingress", {})["path"] = str(value)


__all__ = ["ANCHOR", "run"]
