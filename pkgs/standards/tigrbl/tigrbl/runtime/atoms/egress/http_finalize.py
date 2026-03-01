from __future__ import annotations

from typing import Any, MutableMapping

from ... import events as _ev

ANCHOR = _ev.EGRESS_HTTP_FINALIZE


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

    status_code = egress.get("status_code", getattr(ctx, "status_code", None))
    if status_code is None:
        status_code = 200
    status = int(status_code)

    egress["status_code"] = status
    setattr(ctx, "status_code", status)


__all__ = ["ANCHOR", "run"]
