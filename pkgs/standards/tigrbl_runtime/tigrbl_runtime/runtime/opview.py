from __future__ import annotations
from typing import Any

import warnings

from tigrbl_atoms._opview_helpers import (
    _ensure_temp as _atoms_ensure_temp,
    _ensure_ov as _atoms_ensure_ov,
)

_DEPRECATION = (
    "tigrbl_runtime.runtime.opview is deprecated and will be removed in a future "
    "release; import from tigrbl_atoms._opview_helpers (or atom-local schema "
    "collect logic) instead."
)

warnings.warn(_DEPRECATION, DeprecationWarning, stacklevel=2)


def _ensure_temp(ctx: Any) -> dict[str, Any]:
    warnings.warn(_DEPRECATION, DeprecationWarning, stacklevel=2)
    return _atoms_ensure_temp(ctx)


def _ensure_ov(ctx: Any):
    warnings.warn(_DEPRECATION, DeprecationWarning, stacklevel=2)
    return _atoms_ensure_ov(ctx)


__all__ = ["_ensure_ov", "_ensure_temp"]
