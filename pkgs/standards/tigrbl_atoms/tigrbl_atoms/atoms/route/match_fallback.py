from __future__ import annotations

from typing import Any

from ... import events as _ev
from ...stages import Routed
from ...types import Atom, Ctx, RoutedCtx

ANCHOR = _ev.ROUTE_MATCH_FALLBACK


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    route = temp.setdefault("route", {})
    if not isinstance(route, dict):
        route = {}
        temp["route"] = route
    route.setdefault("matched", False)
    route.setdefault("selector", "")
    route.setdefault("path_params", {})


class AtomImpl(Atom[Routed, Routed]):
    name = "route.match_fallback"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Routed]) -> Ctx[Routed]:
        _run(obj, ctx)
        return ctx.promote(
            RoutedCtx, protocol=str(ctx.temp.get("route", {}).get("protocol", "") or "")
        )


INSTANCE = AtomImpl()
