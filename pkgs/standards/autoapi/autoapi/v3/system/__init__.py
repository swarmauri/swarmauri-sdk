# autoapi/v3/system/__init__.py
"""
AutoAPI v3 – System/Diagnostics helpers.

- attach_diagnostics(api, *, get_db=None, get_async_db=None) -> APIRouter
"""

from __future__ import annotations

from .diagnostics import attach_diagnostics

__all__ = ["attach_diagnostics"]
