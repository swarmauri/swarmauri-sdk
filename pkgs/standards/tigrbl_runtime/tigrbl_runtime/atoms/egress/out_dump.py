from __future__ import annotations

from typing import Any, MutableMapping

from ... import events as _ev

ANCHOR = _ev.EGRESS_OUT_DUMP


def _ensure_temp(ctx: Any) -> MutableMapping[str, Any]:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    return temp


def run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = _ensure_temp(ctx)
    egress = temp.setdefault("egress", {})
    if "wire_payload" in egress:
        return

    wire_payload = temp.get("response_payload")
    if wire_payload is None:
        wire_payload = egress.get("result", getattr(ctx, "result", None))

    if wire_payload is not None:
        egress["wire_payload"] = wire_payload


__all__ = ["ANCHOR", "run"]
