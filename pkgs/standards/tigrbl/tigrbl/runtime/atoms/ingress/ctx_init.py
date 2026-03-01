from __future__ import annotations

from time import perf_counter
from typing import Any, MutableMapping

from ... import events as _ev

ANCHOR = _ev.INGRESS_CTX_INIT


def _ensure_temp(ctx: Any) -> MutableMapping[str, Any]:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    return temp


def run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = _ensure_temp(ctx)
    ingress = temp.setdefault("ingress", {})
    ingress.setdefault("ctx_initialized", True)
    ingress.setdefault("started_at", perf_counter())


__all__ = ["ANCHOR", "run"]
