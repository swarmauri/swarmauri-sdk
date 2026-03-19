from __future__ import annotations

from typing import Any

from ...types import Atom, Ctx, OperatedCtx
from ...stages import Operated

from ... import events as _ev
from .._temp import _ensure_temp
from ._db import _in_transaction, _resolve_db_handle

ANCHOR = _ev.SYS_TX_COMMIT


async def _run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = _ensure_temp(ctx)
    db = _resolve_db_handle(ctx)
    open_flag = bool(temp.get("__sys_tx_open__")) or (
        db is not None and _in_transaction(db)
    )

    try:
        if not open_flag or db is None:
            return
        commit = getattr(db, "commit", None)
        if callable(commit):
            rv = commit()
            if hasattr(rv, "__await__"):
                await rv
    finally:
        temp["__sys_tx_open__"] = False
        release = temp.pop("__sys_db_release__", None)
        if callable(release):
            release()


class AtomImpl(Atom[Operated, Operated]):
    name = "sys.commit_tx"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Operated]) -> Ctx[Operated]:
        await _run(obj, ctx)
        return ctx.promote(OperatedCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
