# tigrbl/v3/transport/jsonrpc/__init__.py
"""
Tigrbl v3 – JSON-RPC transport.

Public helper:
  - build_jsonrpc_router(
        router, *, get_db=None, tags=("rpc",)
    ) -> Router
  - build_openrpc_spec(router) -> dict

Usage:
    from tigrbl.transport.jsonrpc import build_jsonrpc_router
    app.include_router(build_jsonrpc_router(router), prefix="/rpc")
    # OpenRPC schema (JSON-RPC equivalent of OpenAPI)
    build_openrpc_spec(router)
"""

from __future__ import annotations

from .dispatcher import build_jsonrpc_router
from .openrpc import build_openrpc_spec

__all__ = ["build_jsonrpc_router", "build_openrpc_spec"]
