from __future__ import annotations

from typing import Any

from ...types import Atom, Ctx, ExecutingCtx
from ...stages import Guarded, Executing

from ... import events as _ev
from .._temp import _ensure_temp
from ._db import _resolve_db_handle

ANCHOR = _ev.SYS_TX_BEGIN


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
        return ctx.promote(ExecutingCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
