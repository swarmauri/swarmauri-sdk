"""Deprecated access point for JSON Schemas."""

from __future__ import annotations

import warnings

from peagen.jsonschemas import *  # noqa: F401,F403

warnings.warn(
    "peagen.schemas is deprecated; use peagen.jsonschemas instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [name for name in globals() if name.isupper()]
