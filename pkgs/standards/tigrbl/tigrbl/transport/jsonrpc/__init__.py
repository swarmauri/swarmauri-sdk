# tigrbl/v3/transport/jsonrpc/__init__.py
"""
Tigrbl v3 – JSON-RPC transport.

Public helper:
  - build_jsonrpc_router(
        api, *, get_db=None, tags=("rpc",)
    ) -> Router

Usage:
    from tigrbl.transport.jsonrpc import build_jsonrpc_router
    app.include_router(build_jsonrpc_router(api), prefix="/rpc")
"""

from __future__ import annotations

from .dispatcher import build_jsonrpc_router

__all__ = ["build_jsonrpc_router"]
