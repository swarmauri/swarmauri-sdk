from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.ROUTE_PROTOCOL_DETECT


def run(obj: object | None, ctx: Any) -> None:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    request = getattr(ctx, "request", None)
    scope = getattr(request, "scope", None) if request is not None else None
    protocol = scope.get("type") if isinstance(scope, dict) else None
    if protocol is None and request is not None:
        protocol = getattr(request, "protocol", None)
    if protocol is None:
        raw = getattr(ctx, "raw", None)
        raw_scope = getattr(raw, "scope", None) if raw is not None else None
        if isinstance(raw_scope, dict):
            protocol = raw_scope.get("type")
    if protocol is not None:
        temp.setdefault("route", {})["protocol"] = protocol
        setattr(ctx, "proto", protocol)


__all__ = ["ANCHOR", "run"]
