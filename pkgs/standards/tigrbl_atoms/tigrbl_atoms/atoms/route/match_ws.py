from __future__ import annotations

from typing import Any, Mapping

from ... import events as _ev
from ...stages import Routed, Bound
from ...types import Atom, BoundCtx, Ctx

ANCHOR = getattr(_ev, "ROUTE_MATCH_WS", "route.match.ws")


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

    candidates = route.get("protocol_candidates")
    if not isinstance(candidates, list):
        return

    ws_proto = next(
        (p for p in candidates if isinstance(p, str) and p in {"ws", "wss"}), None
    )
    if not isinstance(ws_proto, str):
        return

    route["protocol"] = ws_proto
    setattr(ctx, "proto", ws_proto)
    setattr(ctx, "protocol", ws_proto)

    plan = getattr(ctx, "kernel_plan", None) or getattr(ctx, "plan", None)
    if plan is None:
        return

    proto_indices = getattr(plan, "proto_indices", None)
    if not isinstance(proto_indices, Mapping):
        return

    index = proto_indices.get(ws_proto)
    if not isinstance(index, Mapping):
        return

    path = str(getattr(ctx, "path", "") or "")
    if not path:
        return

    meta_index = index.get(path)
    if isinstance(meta_index, int):
        route["matched"] = True
        route["binding"] = meta_index
        route["opmeta_index"] = meta_index
        route["selector"] = path
        setattr(ctx, "binding", meta_index)
        setattr(ctx, "selector", path)


class AtomImpl(Atom[Routed, Bound]):
    name = "route.match_ws"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Routed]) -> Ctx[Bound]:
        _run(obj, ctx)
        return ctx.promote(
            BoundCtx,
            protocol=str(ctx.temp.get("route", {}).get("protocol", "") or ""),
            binding=ctx.temp.get("route", {}).get("binding"),
        )


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
