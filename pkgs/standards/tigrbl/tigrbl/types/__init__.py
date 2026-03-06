"""Compatibility re-export for split typing package."""

from __future__ import annotations

import warnings

from tigrbl_typing import types as _types
from tigrbl_typing.types import *  # noqa: F401,F403

__all__ = list(_types.__all__)

_DEPRECATED_EXPORTS: dict[str, tuple[str, str]] = {
    "Router": ("tigrbl", "Router"),
    "Request": ("tigrbl", "Request"),
    "Body": ("tigrbl.core.crud", "Body"),
    "Depends": ("tigrbl.security", "Depends"),
    "HTTPException": ("tigrbl.runtime.status", "HTTPException"),
    "Response": ("tigrbl", "Response"),
}


def __getattr__(name: str):
    if name in _DEPRECATED_EXPORTS:
        module, _attr = _DEPRECATED_EXPORTS[name]
        warnings.warn(
            (
                f"tigrbl.types.{name} is deprecated and no longer exports from "
                "tigrbl.types. "
                f"Import it from '{module}' instead."
            ),
            DeprecationWarning,
            stacklevel=2,
        )
        raise AttributeError(
            f"tigrbl.types.{name} no longer exports from tigrbl.types. "
            f"Import it from '{module}' instead."
        )
    return getattr(_types, name)
