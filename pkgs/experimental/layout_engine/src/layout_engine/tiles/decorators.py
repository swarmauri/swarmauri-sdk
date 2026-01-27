from __future__ import annotations
from functools import wraps
from .spec import TileSpec


def tile_ctx(*, id: str, role: str = "generic", **kwargs):
    """Decorator to attach a TileSpec to a factory function.

    Example:
        @tile_ctx(id="kpi_revenue", role="kpi", min_w=240)
        def revenue_tile(): return {"source": "metrics.revenue"}
    """
    spec = TileSpec(id=id, role=role, **kwargs)

    def deco(fn):
        setattr(fn, "__tile_spec__", spec)

        @wraps(fn)
        def wrapper(*a, **kw):
            return fn(*a, **kw)

        return wrapper

    return deco


def tile(*, id: str, role: str = "generic", **kwargs):
    """Backward compatible alias for :func:`tile_ctx`."""
    return tile_ctx(id=id, role=role, **kwargs)


def validate_spec(fn):
    """Placeholder decorator to validate function-provided specs at call-time.

    If the function returns a dict with 'id'/'role', attempt to build a TileSpec for validation.
    Otherwise, pass-through.
    """

    @wraps(fn)
    def wrapper(*a, **kw):
        out = fn(*a, **kw)
        if isinstance(out, dict):
            # If it looks like a spec, validate
            if "id" in out and "role" in out:
                TileSpec(**out)  # will raise on invalid
        return out

    return wrapper
