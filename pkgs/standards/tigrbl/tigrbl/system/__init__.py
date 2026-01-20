# tigrbl/v3/system/__init__.py
"""
Tigrbl v3 – System/Diagnostics helpers.

- mount_diagnostics(api, *, get_db=None) -> Router
"""

from __future__ import annotations

from .diagnostics import mount_diagnostics
from .uvicorn import stop_uvicorn_server

__all__ = ["mount_diagnostics", "stop_uvicorn_server"]
