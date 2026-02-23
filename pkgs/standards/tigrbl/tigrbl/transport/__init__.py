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


def build_jsonrpc_router(*args: Any, **kwargs: Any):
    from .jsonrpc import build_jsonrpc_router as _build_jsonrpc_router

    return _build_jsonrpc_router(*args, **kwargs)


def build_openrpc_spec(*args: Any, **kwargs: Any):
    from .jsonrpc import build_openrpc_spec as _build_openrpc_spec

    return _build_openrpc_spec(*args, **kwargs)


def build_rest_router(*args: Any, **kwargs: Any):
    from .rest import build_rest_router as _build_rest_router

    return _build_rest_router(*args, **kwargs)


def mount_rest(*args: Any, **kwargs: Any):
    from .rest import mount_rest as _mount_rest

    return _mount_rest(*args, **kwargs)


def mount_jsonrpc(
    api: Any,
    app: Any,
    *,
    prefix: str = "/rpc",
    get_db: Optional[Callable[..., Any]] = None,
    tags: Sequence[str] | None = ("rpc",),
):
    """
    Build a JSON-RPC router for `api` and include it on the given ASGI `app`
    (or any object exposing `include_router`).

    Returns the created router so you can keep a reference if desired.

    Parameters
    ----------
    tags:
        Optional tags applied to the mounted "/rpc" endpoint. Defaults to
        ``("rpc",)``.
    """
    normalized_prefix = prefix if str(prefix).startswith("/") else f"/{prefix}"
    setattr(api, "jsonrpc_prefix", normalized_prefix.rstrip("/") or "/")

    router = build_jsonrpc_router(api, get_db=get_db, tags=tags)
    include_router = getattr(app, "include_router", None)
    if callable(include_router):
        include_router(router, prefix=normalized_prefix)

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
