"""Deprecated access point for schema models.

Import from :mod:`peagen.schemas` instead.
"""

from __future__ import annotations

import warnings

from peagen.schemas import *  # noqa: F401,F403

warnings.warn(
    "peagen.models.schemas is deprecated; use peagen.schemas instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [name for name in globals() if not name.startswith("_")]
