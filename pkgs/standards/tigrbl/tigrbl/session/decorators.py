"""Compatibility wrapper for session decorators.

Canonical decorators live under :mod:`tigrbl.decorators.session`.
"""

from __future__ import annotations

from ..decorators.session import read_only_session, session_ctx

__all__ = ["session_ctx", "read_only_session"]
