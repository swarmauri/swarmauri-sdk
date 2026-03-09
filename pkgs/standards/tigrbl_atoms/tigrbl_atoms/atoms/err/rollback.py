from __future__ import annotations

from typing import Any

ANCHOR = "ON_ROLLBACK"


def _resolve_db_handle(ctx: Any) -> Any:
    db = getattr(ctx, "db", None)
    if db is not None:
        return db
    return getattr(ctx, "session", None)


async def run(obj: object | None, ctx: Any) -> None:
    del obj
    db = _resolve_db_handle(ctx)
    if db is None:
        return

    rollback = getattr(db, "rollback", None)
    if callable(rollback):
        rv = rollback()
        if hasattr(rv, "__await__"):
            await rv

    temp = getattr(ctx, "temp", None)
    if isinstance(temp, dict):
        release = temp.pop("__sys_db_release__", None)
        if callable(release):
            release()


__all__ = ["ANCHOR", "run"]
