from __future__ import annotations

import logging
from typing import Dict

from .column_spec import ColumnSpec
from .io_spec import IOSpec
from .storage_spec import StorageSpec

CANONICAL_VERBS = (
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
    "custom",
)

logger = logging.getLogger("uvicorn")


def mro_collect_columns(model: type) -> Dict[str, ColumnSpec]:
    """Collect ColumnSpecs declared on *model* and all mixins.

    Iterates across the model's MRO so that mixin-defined columns are included
    in the resulting mapping. Later definitions take precedence over earlier
    ones in the MRO.
    """
    logger.info("Collecting columns for %s", model.__name__)
    out: Dict[str, ColumnSpec] = {}
    for base in reversed(model.__mro__):
        mapping = getattr(base, "__autoapi_colspecs__", None)
        if isinstance(mapping, dict):
            out.update(mapping)
        mapping = getattr(base, "__autoapi_cols__", None)
        if isinstance(mapping, dict):
            out.update(mapping)

    table = getattr(model, "__table__", None)
    if table is not None:
        for col in getattr(table, "columns", []):
            name = getattr(col, "key", None) or getattr(col, "name", None)
            if not name or name in out:
                continue
            io = IOSpec(in_verbs=CANONICAL_VERBS, out_verbs=CANONICAL_VERBS)
            storage = StorageSpec(
                type_=getattr(col, "type", None),
                nullable=getattr(col, "nullable", None),
                unique=bool(getattr(col, "unique", False)),
                index=bool(getattr(col, "index", False)),
                primary_key=bool(getattr(col, "primary_key", False)),
                autoincrement=getattr(col, "autoincrement", None),
                default=getattr(getattr(col, "default", None), "arg", None),
                onupdate=getattr(col, "onupdate", None),
                server_default=getattr(col, "server_default", None),
                comment=getattr(col, "comment", None),
            )
            out[name] = ColumnSpec(storage=storage, io=io)

    logger.info("Collected %d columns for %s", len(out), model.__name__)
    return out


__all__ = ["mro_collect_columns"]
