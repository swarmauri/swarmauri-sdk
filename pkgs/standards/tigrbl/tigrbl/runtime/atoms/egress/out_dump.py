from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.EGRESS_OUT_DUMP


def run(obj: object | None, ctx: Any) -> None:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    egress = temp.setdefault("egress", {})
    if "wire_payload" not in egress:
        egress["wire_payload"] = egress.get("result", getattr(ctx, "result", None))


__all__ = ["ANCHOR", "run"]
