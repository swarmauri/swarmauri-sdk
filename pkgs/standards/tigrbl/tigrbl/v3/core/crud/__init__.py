from .ops import (
    create,
    read,
    update,
    replace,
    merge,
    delete,
    list as _list,
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
