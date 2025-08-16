"""
AutoAPI v2 Implementation Package

This package contains the modular implementation components for AutoAPI v2,
organized into focused modules for better maintainability and testing.

Modules:
- schema: Schema generation and caching
- crud_builder: CRUD operations and database handling
- rpc_adapter: RPC parameter adaptation and response formatting
- routes_builder: REST and RPC route building
"""

from __future__ import annotations

# Main function imports - only the core functions needed by AutoAPI
from .schema import _build_schema
from .crud_builder import _crud
from .rpc_adapter import _wrap_rpc
from .routes_builder import _register_routes_and_rpcs
from ._runner import _invoke, _Ctx

# Legacy helpers (kept for backward compatibility)
from inspect import isawaitable


async def _run(core, *a):
    """Legacy helper for running potentially async functions."""
    print(f"_run invoked with core={core} args={a}")
    rv = core(*a)
    if isawaitable(rv):
        print("_run awaiting async result")
        rv = await rv
    print(f"_run returning {rv}")
    return rv


def _commit_or_flush(self, db) -> None:
    """Legacy helper for commit or flush."""
    action = "flush" if db.in_nested_transaction() else "commit"
    print(f"_commit_or_flush performing {action}")
    db.flush() if db.in_nested_transaction() else db.commit()
    print("_commit_or_flush done")


# Export only the main functions that are needed by the AutoAPI class
__all__ = [
    "_build_schema",
    "_crud",
    "_wrap_rpc",
    "_register_routes_and_rpcs",
    "_run",
    "_commit_or_flush",
    "_Ctx",
    "_invoke",
]
