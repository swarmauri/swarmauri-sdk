from __future__ import annotations

from typing import Any, Mapping

from ... import events as _ev
from ...stages import Bound
from ...types import Atom, BoundCtx, Ctx

ANCHOR = _ev.ROUTE_PARAMS_NORMALIZE


def _as_dict(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        return {}
    return {str(k): v for k, v in value.items()}


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)

    route = temp.setdefault("route", {})
    ingress = temp.get("ingress") if isinstance(temp.get("ingress"), dict) else {}

    path_params = _as_dict(route.get("path_params"))
    query_params = _as_dict(ingress.get("query")) if isinstance(ingress, dict) else {}

    route["path_params"] = path_params
    route["query_params"] = query_params
    route["params"] = {**query_params, **path_params}


class AtomImpl(Atom[Bound, Bound]):
    name = "route.params_normalize"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Bound]) -> Ctx[Bound]:
        _run(obj, ctx)
        return ctx.promote(BoundCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
