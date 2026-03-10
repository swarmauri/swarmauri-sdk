from __future__ import annotations

import warnings
from typing import Any, Mapping

from tigrbl_atoms._opview_helpers import (
    _ensure_temp as _atoms_ensure_temp,
    ensure_schema_in as _atoms_ensure_schema_in,
    ensure_schema_out as _atoms_ensure_schema_out,
    opview_from_ctx as _atoms_opview_from_ctx,
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


def opview_from_ctx(ctx: Any):
    warnings.warn(_DEPRECATION, DeprecationWarning, stacklevel=2)
    return _atoms_opview_from_ctx(ctx)


def ensure_schema_in(ctx: Any, ov) -> Mapping[str, Any]:
    warnings.warn(_DEPRECATION, DeprecationWarning, stacklevel=2)
    return _atoms_ensure_schema_in(ctx, ov)


def ensure_schema_out(ctx: Any, ov) -> Mapping[str, Any]:
    warnings.warn(_DEPRECATION, DeprecationWarning, stacklevel=2)
    return _atoms_ensure_schema_out(ctx, ov)


__all__ = ["opview_from_ctx", "ensure_schema_in", "ensure_schema_out", "_ensure_temp"]
