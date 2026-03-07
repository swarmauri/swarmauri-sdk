from __future__ import annotations

from ...types import Atom, Ctx, cast_ctx
from ...stages import Guarded, Executing

from typing import Any

from ... import events as _ev

ANCHOR = _ev.SYS_TX_BEGIN


def _ensure_temp(ctx: Any) -> dict[str, Any]:
    temp = getattr(ctx, "temp", None)
    if isinstance(temp, dict):
        return temp
    temp = {}
    setattr(ctx, "temp", temp)
    return temp


def _resolve_db_handle(ctx: Any) -> Any:
    db = getattr(ctx, "db", None)
    if db is not None:
        return db
    return getattr(ctx, "session", None)


async def _run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = _ensure_temp(ctx)
    db = _resolve_db_handle(ctx)
    temp["__sys_tx_open__"] = db is not None

    if db is None:
        return

    begin = getattr(db, "begin", None)
    if callable(begin):
        rv = begin()
        if hasattr(rv, "__await__"):
            await rv


class AtomImpl(Atom[Guarded, Executing]):
    name = "sys.start_tx"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Guarded]) -> Ctx[Executing]:
        await _run(obj, ctx)
        return cast_ctx(ctx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
