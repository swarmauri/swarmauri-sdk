"""Tigrbl canon compatibility package."""

from __future__ import annotations

import warnings

_DEPRECATION_MESSAGE = (
    "tigrbl_canon is deprecated, not supported anymore, and likely to break. "
    "Migrate away from tigrbl_canon imports as soon as possible."
)

warnings.warn(_DEPRECATION_MESSAGE, DeprecationWarning, stacklevel=2)

__all__ = ["_DEPRECATION_MESSAGE"]
