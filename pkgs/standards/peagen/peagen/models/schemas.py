"""Backward compatibility wrapper for schema models."""

from __future__ import annotations

from peagen.schemas import *  # noqa: F401,F403

__all__ = [name for name in globals() if not name.startswith("_")]
