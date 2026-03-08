from __future__ import annotations

from typing import Any

from ... import events as _ev
from ...stages import Routed, Bound
from ...types import Atom, BoundCtx, Ctx

ANCHOR = getattr(_ev, "ROUTE_MATCH_FALLBACK", "route.match.fallback")


def _route_dict(ctx: Any) -> dict[str, object]:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)

    route_obj = temp.setdefault("route", {})
    if isinstance(route_obj, dict):
        return route_obj

    route: dict[str, object] = {}
    temp["route"] = route
    return route


def _run(obj: object | None, ctx: Any) -> None:
    del obj

    route = _route_dict(ctx)
    if bool(route.get("matched")):
        return

    route.setdefault("binding", None)
    route.setdefault("opmeta_index", None)
    route.setdefault("selector", "")
    route.setdefault("path_params", {})


class AtomImpl(Atom[Routed, Bound]):
    name = "route.match_fallback"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Routed]) -> Ctx[Bound]:
        _run(obj, ctx)
        return ctx.promote(
            BoundCtx,
            protocol=str(ctx.temp.get("route", {}).get("protocol", "") or ""),
            path_params=dict(ctx.temp.get("route", {}).get("path_params", {}) or {}),
            binding=ctx.temp.get("route", {}).get("binding"),
        )


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
