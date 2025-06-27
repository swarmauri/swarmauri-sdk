"""Backwards compatibility shim for :mod:`peagen.schemas`."""

from __future__ import annotations

from warnings import warn

from peagen.schemas import *  # noqa: F401,F403

warn(
    "peagen.models.schemas is deprecated; use peagen.schemas instead",
    DeprecationWarning,
    stacklevel=2,
)
