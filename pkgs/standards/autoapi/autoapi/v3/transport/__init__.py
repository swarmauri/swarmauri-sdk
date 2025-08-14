# autoapi/v3/transport/__init__.py
"""
AutoAPI v3 – Transport package.

Currently provides a JSON-RPC transport. You can either import the router
factory directly, or use the small convenience helper below to mount it.

Example:
    from autoapi.v3.transport import mount_jsonrpc

    mount_jsonrpc(api, app, prefix="/rpc", get_async_db=get_async_session_dep)
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable, Optional

from .jsonrpc import build_jsonrpc_router


def mount_jsonrpc(
    api: Any,
    app: Any,
    *,
    prefix: str = "/rpc",
    get_db: Optional[Callable[..., Any]] = None,
    get_async_db: Optional[Callable[..., Awaitable[Any]]] = None,
):
    """
    Build a JSON-RPC router for `api` and include it on the given FastAPI `app`
    (or any object exposing `include_router`).

    Returns the created router so you can keep a reference if desired.
    """
    router = build_jsonrpc_router(api, get_db=get_db, get_async_db=get_async_db)
    include_router = getattr(app, "include_router", None)
    if callable(include_router):
        include_router(router, prefix=prefix)
    return router


__all__ = ["build_jsonrpc_router", "mount_jsonrpc"]
