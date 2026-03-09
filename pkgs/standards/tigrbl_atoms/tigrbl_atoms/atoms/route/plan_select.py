from __future__ import annotations

from ...types import Atom, Ctx, PlannedCtx
from ...stages import Planned

from typing import Any

from ... import events as _ev

ANCHOR = _ev.ROUTE_PLAN_SELECT


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    route = temp.setdefault("route", {})

    plan = getattr(ctx, "kernel_plan", None) or getattr(ctx, "plan", None)
    maybe_index = route.get("opmeta_index")
    if isinstance(maybe_index, int) and plan is not None:
        chains = getattr(plan, "phase_chains", {})
        if isinstance(chains, dict):
            chain = chains.get(maybe_index)
            if chain is not None:
                route["plan"] = chain
                setattr(ctx, "plan", chain)
                return

    current = getattr(ctx, "plan", None)
    if current is not None:
        route["plan"] = current


class AtomImpl(Atom[Planned, Planned]):
    name = "route.plan_select"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Planned]) -> Ctx[Planned]:
        _run(obj, ctx)
        return ctx.promote(PlannedCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
