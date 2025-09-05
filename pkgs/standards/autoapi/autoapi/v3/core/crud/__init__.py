# autoapi/v3/core/crud/__init__.py
"""Canonical CRUD operations split across submodules."""

from .operations import (
    create,
    read,
    update,
    replace,
    merge,
    delete,
    list as _list,  # noqa: F401
    clear,
)
from .bulk import (
    bulk_create,
    bulk_update,
    bulk_replace,
    bulk_merge,
    bulk_delete,
)

# Public alias named exactly `list` to preserve API surface
list = _list  # noqa: A001

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
