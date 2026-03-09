from __future__ import annotations

from typing import Any, Mapping

from ... import events as _ev
from ...stages import Bound
from ...types import Atom, BoundCtx, Ctx

ANCHOR = _ev.ROUTE_PARAMS_NORMALIZE


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


def _to_plain_dict(value: object) -> dict[str, object]:
    if isinstance(value, Mapping):
        return {str(k): v for k, v in value.items()}
    return {}


def _query_params(ctx: Any) -> dict[str, object]:
    qp = getattr(ctx, "query_params", None)
    if isinstance(qp, Mapping):
        return {str(k): v for k, v in qp.items()}

    request = getattr(ctx, "request", None)
    if request is not None:
        maybe = getattr(request, "query_params", None)
        if isinstance(maybe, Mapping):
            return {str(k): v for k, v in maybe.items()}

    gw_raw = getattr(ctx, "gw_raw", None)
    if gw_raw is not None:
        maybe = getattr(gw_raw, "query", None)
        if isinstance(maybe, Mapping):
            return {str(k): v for k, v in maybe.items()}

    return {}


def _normalize_scalar(value: object) -> object:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, list):
        return [_normalize_scalar(item) for item in value]
    if isinstance(value, tuple):
        return [_normalize_scalar(item) for item in value]
    if isinstance(value, Mapping):
        return {str(k): _normalize_scalar(v) for k, v in value.items()}
    return value


def _run(obj: object | None, ctx: Any) -> None:
    del obj

    route = _route_dict(ctx)

    path_params = _to_plain_dict(route.get("path_params"))
    query_params = _query_params(ctx)

    normalized_path = {str(k): _normalize_scalar(v) for k, v in path_params.items()}
    normalized_query = {str(k): _normalize_scalar(v) for k, v in query_params.items()}

    params: dict[str, object] = {}
    params.update(normalized_query)
    params.update(normalized_path)

    route["path_params"] = normalized_path
    route["query_params"] = normalized_query
    route["params"] = params


class AtomImpl(Atom[Bound, Bound]):
    name = "route.params_normalize"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Bound]) -> Ctx[Bound]:
        _run(obj, ctx)
        return ctx.promote(
            BoundCtx,
            protocol=str(ctx.temp.get("route", {}).get("protocol", "") or ""),
            path_params=dict(ctx.temp.get("route", {}).get("path_params", {}) or {}),
            binding=ctx.temp.get("route", {}).get("binding"),
        )


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
