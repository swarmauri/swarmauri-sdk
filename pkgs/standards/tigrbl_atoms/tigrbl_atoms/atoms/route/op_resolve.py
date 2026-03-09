from __future__ import annotations

from typing import Any

from ... import events as _ev
from ...stages import Bound, Planned
from ...types import Atom, Ctx, PlannedCtx

ANCHOR = _ev.ROUTE_OP_RESOLVE


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


def _plan(ctx: Any) -> Any:
    return getattr(ctx, "kernel_plan", None) or getattr(ctx, "plan", None)


def _default_status(op_alias: str) -> int:
    alias = op_alias.lower()
    if alias in {"create", "bulk_create"}:
        return 201
    return 200


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    route = _route_dict(ctx)
    binding = route.get("program_id", route.get("opmeta_index", route.get("binding")))
    if not isinstance(binding, int) or binding < 0:
        return
    plan = _plan(ctx)
    if plan is None:
        return
    opmeta = getattr(plan, "opmeta", ())
    if not isinstance(opmeta, (list, tuple)) or binding >= len(opmeta):
        return
    meta = opmeta[binding]
    route["binding"] = binding
    route["program_id"] = binding
    route["opmeta_index"] = binding
    model = getattr(meta, "model", None)
    alias = getattr(meta, "alias", None)
    target = getattr(meta, "target", None)
    setattr(ctx, "model", model)
    setattr(ctx, "op", alias)
    setattr(ctx, "target", target)
    if isinstance(alias, str):
        status_code = _default_status(alias)
        route.setdefault("status_code", status_code)
        setattr(ctx, "status_code", route["status_code"])


class AtomImpl(Atom[Bound, Planned]):
    name = "route.op_resolve"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Bound]) -> Ctx[Planned]:
        _run(obj, ctx)
        return ctx.promote(
            PlannedCtx,
            protocol=str(ctx.temp.get("route", {}).get("protocol", "") or ""),
            path_params=dict(ctx.temp.get("route", {}).get("path_params", {}) or {}),
            binding=ctx.temp.get("route", {}).get("binding"),
            opmeta_index=ctx.temp.get("route", {}).get("opmeta_index"),
        )


INSTANCE = AtomImpl()
