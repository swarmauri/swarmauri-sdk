from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.EGRESS_ENVELOPE_APPLY


def run(obj: object | None, ctx: Any) -> None:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    egress = temp.setdefault("egress", {})
    payload = egress.get("wire_payload")
    if payload is not None:
        egress["enveloped"] = {"data": payload}


__all__ = ["ANCHOR", "run"]
