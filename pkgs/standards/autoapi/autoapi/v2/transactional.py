from functools import wraps
from typing import Any, Callable

from sqlalchemy.orm import Session


def transactional(self, fn: Callable[..., Any]):
    """
    Decorator to wrap an RPC handler in an explicit DB transaction.
    """

    @wraps(fn)
    def wrapper(params, db: Session, *a, **k):
        db.begin()
        try:
            res = fn(params, db, *a, **k)
            db.commit()
            return res
        except Exception:
            db.rollback()
            raise

    return wrapper
