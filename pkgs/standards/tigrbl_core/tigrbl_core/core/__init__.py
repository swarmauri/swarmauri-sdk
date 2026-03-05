# tigrbl/v3/core/__init__.py
"""
Tigrbl v3 – Core operations.

Re-exports the canonical CRUD bodies implemented in `.crud`.

Notes:
- These functions are **flush-only**. They never call `db.commit()`.
- Final commits are driven by the runtime executor's `END_TX` phase.
"""

from __future__ import annotations

from .crud import (
    create,
    read,
    update,
    replace,
    merge,
    delete,
    list as _list,  # avoid shadowing built-in, then re-export as `list`
    clear,
    bulk_create,
    bulk_update,
    bulk_replace,
    bulk_merge,
    bulk_delete,
)

# Public alias named exactly `list` to preserve API surface
list = _list  # noqa: A001 - intentional shadow of built-in for public API

__all__ = [
    "create",
    "read",
    "update",
    "replace",
    "merge",
    "delete",
    "list",
    "clear",
    "bulk_create",
    "bulk_update",
    "bulk_replace",
    "bulk_merge",
    "bulk_delete",
]
