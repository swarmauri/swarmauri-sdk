from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.EGRESS_HTTP_FINALIZE


def run(obj: object | None, ctx: Any) -> None:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    status_code = getattr(ctx, "status_code", None)
    if status_code is not None:
        temp.setdefault("egress", {})["status_code"] = int(status_code)


__all__ = ["ANCHOR", "run"]
