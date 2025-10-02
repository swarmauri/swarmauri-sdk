from __future__ import annotations
from functools import wraps
from typing import Callable
from .spec import Table

def table_defaults(*, gap_x: int | None = None, gap_y: int | None = None):
    """Decorator to enforce/override default gaps on a Table factory.

    Example:
        @table_defaults(gap_x=16, gap_y=12)
        def dashboard() -> Table: ...
    """
    def deco(fn: Callable[..., Table]):
        @wraps(fn)
        def wrapper(*a, **kw) -> Table:
            t = fn(*a, **kw)
            gx = gap_x if gap_x is not None else t.gap_x
            gy = gap_y if gap_y is not None else t.gap_y
            if gx == t.gap_x and gy == t.gap_y:
                return t
            # return a new table with same rows but overridden gaps
            return Table(rows=t.rows, gap_x=gx, gap_y=gy)
        return wrapper
    return deco

def derive_policy(fn: Callable[..., Table]):
    """Placeholder policy decorator retained for backward compatibility."""
    @wraps(fn)
    def wrapper(*a, **kw) -> Table:
        return fn(*a, **kw)
    return wrapper
