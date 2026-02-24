from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.INGRESS_BODY_PEEK


def run(obj: object | None, ctx: Any) -> None:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    ingress = temp.setdefault("ingress", {})
    body = ingress.get("body")
    if isinstance(body, (bytes, bytearray)):
        ingress["body_peek"] = bytes(body[:256])
    elif body is not None:
        ingress["body_peek"] = str(body)[:256]


__all__ = ["ANCHOR", "run"]
