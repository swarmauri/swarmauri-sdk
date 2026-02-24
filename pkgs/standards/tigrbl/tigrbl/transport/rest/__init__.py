# tigrbl/v3/transport/rest/__init__.py
"""
Tigrbl v3 – REST transport wrapper.

Use this when you prefer to mount a single top-level router that aggregates all
model routers (instead of mounting each one inside include_tables).

Typical usage:
    from tigrbl.transport.rest import build_rest_router, mount_rest

    # When including models, skip mounting per-model:
<<<<<<< HEAD
    router.include_table(User, mount_router=False)
    router.include_table(Team, mount_router=False)
    # or:
    router.include_tables([User, Team], mount_router=False)
=======
    router.include_model(User, mount_router=False)
    router.include_model(Team, mount_router=False)
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c

    # Then aggregate & mount once:
    app.include_router(build_rest_router(router, base_prefix="/router"))
    # or:
    mount_rest(router, app, base_prefix="/router")
"""

from __future__ import annotations

from .aggregator import build_rest_router, mount_rest

__all__ = [
    "build_rest_router",
    "mount_rest",
]
