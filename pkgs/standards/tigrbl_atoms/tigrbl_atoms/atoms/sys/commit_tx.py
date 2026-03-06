from __future__ import annotations

from ...types import Atom, Ctx, cast_ctx
from ...stages import Operated

from typing import Any

from ... import events as _ev

ANCHOR = _ev.SYS_TX_COMMIT


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


def _in_transaction(db: Any) -> bool:
    marker = getattr(db, "in_transaction", None)
    if callable(marker):
        try:
            return bool(marker())
        except Exception:
            return False
    return False


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
        return cast_ctx(ctx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
