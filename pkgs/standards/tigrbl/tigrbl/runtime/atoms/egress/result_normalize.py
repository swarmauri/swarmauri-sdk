from __future__ import annotations

from typing import Any, MutableMapping

from ... import events as _ev

ANCHOR = _ev.EGRESS_RESULT_NORMALIZE


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

    if "result" not in egress:
        if hasattr(ctx, "result"):
            egress["result"] = getattr(ctx, "result")
        elif "response_payload" in temp:
            egress["result"] = temp.get("response_payload")


__all__ = ["ANCHOR", "run"]
