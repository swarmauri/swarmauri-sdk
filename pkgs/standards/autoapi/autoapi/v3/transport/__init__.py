# autoapi/v3/transport/__init__.py
"""
AutoAPI v3 – Transport package.

Routers & helpers for exposing your API over JSON-RPC and REST.

Quick usage:
    from autoapi.v3.transport import (
        build_jsonrpc_router, mount_jsonrpc,
        build_rest_router,   mount_rest,
    )

    # JSON-RPC
    app.include_router(build_jsonrpc_router(api), prefix="/rpc")
    # or supply a DB dependency from an Engine or Provider:
    mount_jsonrpc(api, app, prefix="/rpc", engine=my_engine)

    # REST (aggregate all model routers under one prefix)
    # after you include models with mount_router=False
    app.include_router(build_rest_router(api, base_prefix="/api"))
    # or:
    mount_rest(api, app, base_prefix="/api")
"""

from __future__ import annotations

from typing import Any, Sequence

# JSON-RPC transport
from .jsonrpc import build_jsonrpc_router

# REST transport (aggregator over per-model routers)
from .rest import build_rest_router, mount_rest


def mount_jsonrpc(
    api: Any,
    app: Any,
    *,
    prefix: str = "/rpc",
    engine: Any | None = None,
    tags: Sequence[str] | None = ("rpc",),
):
    """
    Build a JSON-RPC router for `api` and include it on the given FastAPI `app`
    (or any object exposing `include_router`).

    Returns the created router so you can keep a reference if desired.

    Parameters
    ----------
    engine:
        Optional engine or provider supplying a ``get_db`` dependency.
    tags:
        Optional tags applied to the mounted "/rpc" endpoint. Defaults to
        ``("rpc",)``.
    """
    dep = engine.get_db if engine is not None else getattr(api, "get_db", None)
    router = build_jsonrpc_router(
        api,
        get_db=dep,
        tags=tags,
    )
    include_router = getattr(app, "include_router", None)
    if callable(include_router):
        include_router(router, prefix=prefix)
    return router


__all__ = [
    # JSON-RPC
    "build_jsonrpc_router",
    "mount_jsonrpc",
    # REST
    "build_rest_router",
    "mount_rest",
]
