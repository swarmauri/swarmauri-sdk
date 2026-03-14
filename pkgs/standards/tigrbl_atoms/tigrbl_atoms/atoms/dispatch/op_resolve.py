from __future__ import annotations

from typing import Any, Mapping

from ... import events as _ev
from ...stages import Bound, Planned
from ...types import Atom, Ctx, PlannedCtx

ANCHOR = _ev.DISPATCH_OP_RESOLVE


def _dispatch_dict(ctx: Any) -> dict[str, object]:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    obj = temp.setdefault("dispatch", {})
    if isinstance(obj, dict):
        return obj
    temp["dispatch"] = {}
    return temp["dispatch"]


def _default_status(op_alias: str) -> int:
    return 201 if op_alias.lower() in {"create", "bulk_create"} else 200


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    dispatch = _dispatch_dict(ctx)
    temp = getattr(ctx, "temp", None)
    route = temp.setdefault("route", {}) if isinstance(temp, dict) else {}
    plan = getattr(ctx, "kernel_plan", None) or getattr(ctx, "plan", None)
    if plan is None:
        return

    selector = dispatch.get("binding_selector")
    protocol = dispatch.get("binding_protocol")
    packed = getattr(plan, "packed", None)
    selector_to_id = getattr(packed, "selector_to_id", {}) if packed is not None else {}
    proto_to_id = getattr(packed, "proto_to_id", {}) if packed is not None else {}
    route_to_program = (
        getattr(packed, "route_to_program", None) if packed is not None else None
    )

    selector_id = (
        selector_to_id.get(selector) if isinstance(selector_to_id, Mapping) else None
    )
    proto_id = proto_to_id.get(protocol) if isinstance(proto_to_id, Mapping) else None
    op_index: int | None = None
    if (
        isinstance(proto_id, int)
        and isinstance(selector_id, int)
        and route_to_program is not None
    ):
        if 0 <= proto_id < len(route_to_program):
            row = route_to_program[proto_id]
            if 0 <= selector_id < len(row):
                maybe = row[selector_id]
                if isinstance(maybe, int) and maybe >= 0:
                    op_index = maybe

    if op_index is None:
        return

    opmeta = getattr(plan, "opmeta", ())
    if not isinstance(opmeta, (list, tuple)) or op_index >= len(opmeta):
        return
    meta = opmeta[op_index]

    dispatch["opmeta_index"] = op_index
    dispatch["binding"] = op_index
    if isinstance(route, dict):
        route["opmeta_index"] = op_index
        route["binding"] = op_index
    setattr(ctx, "binding", op_index)
    setattr(ctx, "opmeta_index", op_index)
    setattr(ctx, "model", getattr(meta, "model", None))
    alias = getattr(meta, "alias", None)
    setattr(ctx, "op", alias)
    setattr(ctx, "target", getattr(meta, "target", None))
    if isinstance(alias, str):
        status = _default_status(alias)
        if isinstance(route, dict):
            route["status_code"] = status
        setattr(ctx, "status_code", status)


class AtomImpl(Atom[Bound, Planned]):
    name = "dispatch.op_resolve"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Bound]) -> Ctx[Planned]:
        _run(obj, ctx)
        return ctx.promote(PlannedCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
