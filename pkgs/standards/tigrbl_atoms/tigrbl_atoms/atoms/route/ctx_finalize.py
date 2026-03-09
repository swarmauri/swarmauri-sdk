from __future__ import annotations

from typing import Any

from ... import events as _ev
from ...stages import Planned
from ...types import Atom, Ctx, PlannedCtx

ANCHOR = _ev.ROUTE_CTX_FINALIZE


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


def _acquire_session(ctx: Any) -> None:
    if (
        getattr(ctx, "db", None) is not None
        or getattr(ctx, "session", None) is not None
    ):
        return

    factory = getattr(ctx, "db_factory", None) or getattr(ctx, "session_factory", None)
    if callable(factory):
        try:
            session = factory()
        except Exception:
            return
        setattr(ctx, "session", session)
        setattr(ctx, "db", session)


def _attach_response_adapter(ctx: Any) -> None:
    if getattr(ctx, "response_adapter", None) is not None:
        return

    adapter_factory = getattr(ctx, "response_adapter_factory", None)
    if callable(adapter_factory):
        try:
            adapter = adapter_factory(ctx)
        except Exception:
            return
        setattr(ctx, "response_adapter", adapter)


def _attach_serializer(ctx: Any) -> None:
    if getattr(ctx, "serializer", None) is not None:
        return

    serializer_factory = getattr(ctx, "serializer_factory", None)
    if callable(serializer_factory):
        try:
            serializer = serializer_factory(ctx)
        except Exception:
            return
        setattr(ctx, "serializer", serializer)


def _run(obj: object | None, ctx: Any) -> None:
    del obj

    route = _route_dict(ctx)

    if not isinstance(route.get("program_id"), int) and not isinstance(route.get("opmeta_index"), int) and route.get("handler") is None:
        return

    _acquire_session(ctx)
    _attach_response_adapter(ctx)
    _attach_serializer(ctx)

    route["finalized"] = True


class AtomImpl(Atom[Planned, Planned]):
    name = "route.ctx_finalize"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Planned]) -> Ctx[Planned]:
        _run(obj, ctx)
        return ctx.promote(
            PlannedCtx,
            protocol=str(ctx.temp.get("route", {}).get("protocol", "") or ""),
            path_params=dict(ctx.temp.get("route", {}).get("path_params", {}) or {}),
            binding=ctx.temp.get("route", {}).get("binding"),
            opmeta_index=ctx.temp.get("route", {}).get("opmeta_index"),
        )


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
