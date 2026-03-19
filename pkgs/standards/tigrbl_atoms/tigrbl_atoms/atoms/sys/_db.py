from __future__ import annotations

import inspect
from functools import lru_cache
from typing import Any, Callable

from sqlalchemy.ext.asyncio import AsyncSession


def _resolve_db_handle(ctx: Any) -> Any:
    db = getattr(ctx, "db", None)
    if db is not None:
        return db
    return getattr(ctx, "session", None)


@lru_cache(maxsize=64)
def _type_is_async_db(db_type: type) -> bool:
    try:
        if issubclass(db_type, AsyncSession):
            return True
    except Exception:
        pass
    for attr in ("commit", "begin", "rollback", "flush"):
        try:
            if inspect.iscoroutinefunction(getattr(db_type, attr, None)):
                return True
        except Exception:
            continue
    return False


def _is_async_db(db: Any) -> bool:
    if db is None:
        return False
    if isinstance(db, AsyncSession):
        return True
    if hasattr(db, "run_sync"):
        return True
    return _type_is_async_db(type(db))


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
