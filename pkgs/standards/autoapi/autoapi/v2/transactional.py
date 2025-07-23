from functools import wraps
from inspect import isawaitable
from typing import Any, Callable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session


def transactional(self, fn: Callable[..., Any]):
    """
    Decorator to wrap an RPC handler in an explicit DB transaction.
    """

    def _sync(params, db: Session, *a, **k):
        db.begin()
        try:
            result = fn(params, db, *a, **k)
            db.commit()
            return result
        except Exception:
            db.rollback()
            raise

    async def _async(params, db: AsyncSession, *a, **k):
        await db.begin()
        try:
            result = fn(params, db, *a, **k)
            if isawaitable(result):
                result = await result
            await db.commit()
            return result
        except Exception:
            await db.rollback()
            raise

    @wraps(fn)
    def wrapper(params, db: Session | AsyncSession, *a, **k):
        return (
            _async(params, db, *a, **k)
            if isinstance(db, AsyncSession)
            else _sync(params, db, *a, **k)
        )

    return wrapper
