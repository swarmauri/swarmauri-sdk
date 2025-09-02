# autoapi/v3/system/__init__.py
"""
AutoAPI v3 – System/Diagnostics helpers.

- mount_diagnostics(api, *, engine=None, prov=None) -> Router
"""

from __future__ import annotations

from .diagnostics import mount_diagnostics

__all__ = ["mount_diagnostics"]
