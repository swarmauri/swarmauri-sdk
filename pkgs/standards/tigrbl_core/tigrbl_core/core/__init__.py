"""Compatibility facade for OLTP operations.

Operation implementations now live in ``tigrbl_ops_oltp``.
"""

from tigrbl_ops_oltp import (  # noqa: F401
    bulk_create,
    bulk_delete,
    bulk_merge,
    bulk_replace,
    bulk_update,
    clear,
    create,
    delete,
    list,
    merge,
    read,
    replace,
    update,
)

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
