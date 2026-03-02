from __future__ import annotations

from typing import Any

from ... import events as _ev
from ....mapping import engine_resolver as _resolver

ANCHOR = _ev.ROUTE_CTX_FINALIZE


def run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    route = temp.setdefault("route", {})
    route["finalized"] = True

    if getattr(ctx, "db", None) is not None:
        return

    model = getattr(ctx, "model", None)
    op_alias = getattr(ctx, "op", None)
    router = getattr(ctx, "router", None) or getattr(ctx, "app", None)
    if model is None or op_alias is None:
        return

    db, release = _resolver.acquire(router=router, model=model, op_alias=op_alias)
    setattr(ctx, "db", db)
    temp["__sys_db_release__"] = release


__all__ = ["ANCHOR", "run"]
