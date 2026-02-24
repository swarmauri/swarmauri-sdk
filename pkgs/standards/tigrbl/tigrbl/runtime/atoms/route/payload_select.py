from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.ROUTE_PAYLOAD_SELECT


def run(obj: object | None, ctx: Any) -> None:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    payload = getattr(ctx, "payload", None)
    if payload is None:
        ingress = temp.get("ingress") if isinstance(temp.get("ingress"), dict) else {}
        payload = ingress.get("body") if isinstance(ingress, dict) else None
    if payload is not None:
        temp.setdefault("route", {})["payload"] = payload


__all__ = ["ANCHOR", "run"]
