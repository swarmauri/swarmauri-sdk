from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.INGRESS_BODY_READ


def run(obj: object | None, ctx: Any) -> None:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    body = getattr(ctx, "body", None)
    if body is not None:
        temp.setdefault("ingress", {})["body"] = body


__all__ = ["ANCHOR", "run"]
