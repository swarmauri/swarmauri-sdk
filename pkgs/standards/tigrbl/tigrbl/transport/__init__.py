# tigrbl/v3/transport/__init__.py
"""
Tigrbl v3 – Transport package.

Routers & helpers for exposing your API over JSON-RPC and REST.

Quick usage:
    from tigrbl.transport import (
        build_jsonrpc_router, mount_jsonrpc,
        build_rest_router,   mount_rest,
    )

    # JSON-RPC
    app.include_router(build_jsonrpc_router(api), prefix="/rpc")
    # or supply a DB dependency from an Engine or Provider:
    mount_jsonrpc(api, app, prefix="/rpc", get_db=my_engine.get_db)

    # REST (aggregate all model routers under one prefix)
    # after you include models with mount_router=False
    app.include_router(build_rest_router(api, base_prefix="/api"))
    # or:
    mount_rest(api, app, base_prefix="/api")
"""

from __future__ import annotations

from typing import Any, Callable, Optional, Sequence
from dataclasses import replace
import re

# JSON-RPC transport
from .jsonrpc import build_jsonrpc_router, build_openrpc_spec

# REST transport (aggregator over per-model routers)
from .rest import build_rest_router, mount_rest


def mount_jsonrpc(
    api: Any,
    app: Any,
    *,
    prefix: str = "/rpc",
    get_db: Optional[Callable[..., Any]] = None,
    tags: Sequence[str] | None = ("rpc",),
):
    """
    Build a JSON-RPC router for `api` and include it on the given FastAPI `app`
    (or any object exposing `include_router`).

    Returns the created router so you can keep a reference if desired.

    Parameters
    ----------
    tags:
        Optional tags applied to the mounted "/rpc" endpoint. Defaults to
        ``("rpc",)``.
    """
    router = build_jsonrpc_router(
        api,
        get_db=get_db,
        tags=tags,
    )
    include_router = getattr(app, "include_router", None)
    if callable(include_router):
        include_router(router, prefix=prefix)

    # Compatibility alias: some router backends normalize empty-path routes to
    # ``<prefix>/`` only. Duplicate JSON-RPC POST routes at ``<prefix>``.
    alias_path = prefix.rstrip("/") or "/"
    if alias_path != "/":
        app_routes = getattr(app, "routes", None)
        if isinstance(app_routes, list):
            escaped = re.escape(alias_path)
            matched = [
                route
                for route in app_routes
                if "POST" in (getattr(route, "methods", ()) or ())
                and getattr(route, "name", None) in {"jsonrpc", "jsonrpc_alt"}
                and getattr(getattr(route, "pattern", None), "pattern", None)
                == f"^{escaped}/$"
            ]
            for route in matched:
                app_routes.append(
                    replace(
                        route,
                        path_template=alias_path,
                        pattern=re.compile(f"^{escaped}$"),
                        name=f"{getattr(route, 'name', 'jsonrpc')}_no_slash",
                        include_in_schema=False,
                    )
                )
    return router


__all__ = [
    # JSON-RPC
    "build_jsonrpc_router",
    "build_openrpc_spec",
    "mount_jsonrpc",
    # REST
    "build_rest_router",
    "mount_rest",
]
