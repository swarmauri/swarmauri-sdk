# tigrbl/v3/transport/rest/__init__.py
"""
Tigrbl v3 – REST transport wrapper.

Use this when you prefer to mount a single top-level router that aggregates all
model routers (instead of mounting each one inside include_model).

Typical usage:
    from tigrbl.transport.rest import build_rest_router, mount_rest

    # When including models, skip mounting per-model:
    router.include_model(User, mount_router=False)
    router.include_model(Team, mount_router=False)

    # Then aggregate & mount once:
    app.include_router(build_rest_router(router, base_prefix="/router"))
    # or:
    mount_rest(router, app, base_prefix="/router")
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
