from __future__ import annotations

from ...types import Atom, Ctx, cast_ctx
from ...stages import Boot, Boot

from time import perf_counter, perf_counter_ns
from typing import Any, MutableMapping

from ... import events as _ev

ANCHOR = _ev.INGRESS_METRICS_START


def _ensure_temp(ctx: Any) -> MutableMapping[str, Any]:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    return temp


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = _ensure_temp(ctx)
    metrics = temp.setdefault("metrics", {})
    metrics.setdefault("ingress_started_at", perf_counter())
    metrics.setdefault("ingress_started_ns", perf_counter_ns())




class AtomImpl(Atom[Boot, Boot]):
    name = "ingress.metrics_start"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Boot]) -> Ctx[Boot]:
        _run(obj, ctx)
        return cast_ctx(ctx)

INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
