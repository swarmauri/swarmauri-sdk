from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.EGRESS_HEADERS_APPLY


def run(obj: object | None, ctx: Any) -> None:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    headers = getattr(ctx, "response_headers", None)
    if headers is None:
        headers = {}
    temp.setdefault("egress", {})["headers"] = dict(headers)


__all__ = ["ANCHOR", "run"]
