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
