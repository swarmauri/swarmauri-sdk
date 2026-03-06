from __future__ import annotations

from ...types import Atom, Ctx, cast_ctx
from ...stages import Bound, Bound

from typing import Any

from ... import events as _ev

ANCHOR = _ev.ROUTE_PATH_PARAMS_EXTRACT


def _run(obj: object | None, ctx: Any) -> None:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    request = getattr(ctx, "request", None)
    path_params = getattr(request, "path_params", None) if request is not None else None
    if path_params:
        temp.setdefault("route", {})["path_params"] = dict(path_params)




class AtomImpl(Atom[Bound, Bound]):
    name = "route.path_params_extract"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Bound]) -> Ctx[Bound]:
        _run(obj, ctx)
        return cast_ctx(ctx)

INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
