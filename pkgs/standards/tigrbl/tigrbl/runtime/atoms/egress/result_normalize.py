from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.EGRESS_RESULT_NORMALIZE


def run(obj: object | None, ctx: Any) -> None:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    result = getattr(ctx, "result", None)
    if result is not None:
        temp.setdefault("egress", {})["result"] = result


__all__ = ["ANCHOR", "run"]
