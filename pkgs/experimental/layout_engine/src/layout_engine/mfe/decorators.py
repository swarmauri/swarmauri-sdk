from __future__ import annotations
from functools import wraps

def remote_ctx(id: str):
    """Decorator to tag a function/factory with a remote_ctx id for discovery."""
    def deco(fn):
        @wraps(fn)
        def wrapper(*a, **kw): return fn(*a, **kw)
        setattr(wrapper, "__remote_id__", id)
        return wrapper
    return deco

def stable_entry(fn):
    """Marker that the remote_ctx entry URL must be immutable (e.g., contains a version)."""
    @wraps(fn)
    def wrapper(*a, **kw): return fn(*a, **kw)
    setattr(wrapper, "__remote_stable_entry__", True)
    return wrapper

def require_integrity(fn):
    """Marker that the remote_ctx should provide SRI integrity."""
    @wraps(fn)
    def wrapper(*a, **kw): return fn(*a, **kw)
    setattr(wrapper, "__remote_require_integrity__", True)
    return wrapper
