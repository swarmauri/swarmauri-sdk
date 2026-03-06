from __future__ import annotations

from ...types import Atom, Ctx, cast_ctx
from ...stages import Bound, Prepared

from typing import Any

from ... import events as _ev

ANCHOR = _ev.ROUTE_PARAMS_NORMALIZE


def _run(obj: object | None, ctx: Any) -> None:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    route = temp.setdefault("route", {})
    params = route.get("path_params") or {}
    ingress = temp.get("ingress") if isinstance(temp.get("ingress"), dict) else {}
    query = ingress.get("query") if isinstance(ingress, dict) else {}
    route["params"] = {**dict(query or {}), **dict(params or {})}




class AtomImpl(Atom[Bound, Prepared]):
    name = "route.params_normalize"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Bound]) -> Ctx[Prepared]:
        _run(obj, ctx)
        return cast_ctx(ctx)

INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
