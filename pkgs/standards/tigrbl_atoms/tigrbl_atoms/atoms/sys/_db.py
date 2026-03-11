from __future__ import annotations

import inspect
from typing import Any, Callable


def _resolve_db_handle(ctx: Any) -> Any:
    db = getattr(ctx, "db", None)
    if db is not None:
        return db
    return getattr(ctx, "session", None)


def _is_async_db(db: Any) -> bool:
    if db is None:
        return False
    if hasattr(db, "run_sync"):
        return True
    for attr in ("commit", "begin", "rollback", "flush"):
        if inspect.iscoroutinefunction(getattr(db, attr, None)):
            return True
    return False


def _bool_call(meth: Callable[..., Any]) -> bool:
    try:
        return bool(meth())
    except Exception:
        return False


def _in_transaction(db: Any) -> bool:
    if db is None:
        return False
    for name in ("in_transaction", "in_nested_transaction"):
        attr = getattr(db, name, None)
        if callable(attr):
            if _bool_call(attr):
                return True
        elif attr:
            return True
    return False


__all__ = ["_resolve_db_handle", "_is_async_db", "_in_transaction"]
