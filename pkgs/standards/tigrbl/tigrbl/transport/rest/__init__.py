# tigrbl/v3/transport/rest/__init__.py
"""
Tigrbl v3 – REST transport wrapper.

Use this when you prefer to mount a single top-level router that aggregates all
model routers (instead of mounting each one inside include_table).

Typical usage:
    from tigrbl.transport.rest import build_rest_router, mount_rest

    # When including models, skip mounting per-model:
    api.include_table(User, mount_router=False)
    api.include_table(Team, mount_router=False)

    # Then aggregate & mount once:
    app.include_router(build_rest_router(api, base_prefix="/api"))
    # or:
    mount_rest(api, app, base_prefix="/api")
"""

from __future__ import annotations

from .aggregator import build_rest_router, mount_rest
from .decorators import delete, get, patch, post, put

__all__ = [
    "build_rest_router",
    "mount_rest",
    "get",
    "post",
    "put",
    "patch",
    "delete",
]
