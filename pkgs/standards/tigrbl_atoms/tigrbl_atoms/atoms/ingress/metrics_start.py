from __future__ import annotations

from ...types import Atom, Ctx, BootCtx
from ...stages import Boot

from time import perf_counter, perf_counter_ns
from typing import Any

from ... import events as _ev
from .._temp import _ensure_temp

ANCHOR = _ev.INGRESS_METRICS_START


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
        return ctx.promote(BootCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
