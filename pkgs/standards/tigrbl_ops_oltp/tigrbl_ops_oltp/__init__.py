"""OLTP operation executors for Tigrbl."""

from .crud import (  # noqa: F401
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
from .executors import dispatch, register_executor, resolve_executor

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
    "resolve_executor",
    "register_executor",
    "dispatch",
]
