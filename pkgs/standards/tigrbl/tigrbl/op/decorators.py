"""Compatibility wrapper for op decorators."""

from ..decorators.op import *  # noqa: F401,F403
from ..decorators.op import (  # noqa: F401
    _ensure_cm as _ensure_cm,
    _infer_arity as _infer_arity,
    _maybe_await as _maybe_await,
    _normalize_persist as _normalize_persist,
    _unwrap as _unwrap,
)
