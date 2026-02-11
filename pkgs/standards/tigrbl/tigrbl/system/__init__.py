# tigrbl/v3/system/__init__.py
"""
Tigrbl v3 – System/Diagnostics helpers.

- mount_diagnostics(api, *, get_db=None) -> Router
"""

from __future__ import annotations

from .diagnostics import mount_diagnostics
from .docs import mount_lens, mount_openapi, mount_openrpc, mount_swagger
from .favicon import FAVICON_PATH
from .uvicorn import stop_uvicorn_server

__all__ = [
    "FAVICON_PATH",
    "mount_diagnostics",
    "mount_lens",
    "mount_openapi",
    "mount_openrpc",
    "mount_swagger",
    "stop_uvicorn_server",
]
