from __future__ import annotations

from typing import Any

from ... import events as _ev
from ...stages import Bound
from ...types import Atom, BoundCtx, Ctx

ANCHOR = _ev.ROUTE_PROGRAM_RESOLVE


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
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)

    proto_id = temp.get("proto_id", route.get("proto_id"))
    selector_id = temp.get("selector_id", route.get("selector_id"))
    plan = getattr(ctx, "kernel_plan", None) or getattr(ctx, "plan", None)
    packed = getattr(plan, "packed", None) if plan is not None else None
    route_to_program = (
        getattr(packed, "route_to_program", None) if packed is not None else None
    )

    program_id = -1
    if (
        isinstance(proto_id, int)
        and isinstance(selector_id, int)
        and route_to_program is not None
    ):
        if 0 <= proto_id < len(route_to_program):
            row = route_to_program[proto_id]
            if 0 <= selector_id < len(row):
                maybe = row[selector_id]
                if isinstance(maybe, int):
                    program_id = int(maybe)

    route["program_id"] = program_id
    temp["program_id"] = program_id
    if program_id >= 0:
        route["binding"] = program_id
        route["opmeta_index"] = program_id
        setattr(ctx, "binding", program_id)


class AtomImpl(Atom[Bound, Bound]):
    name = "route.program_resolve"
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
