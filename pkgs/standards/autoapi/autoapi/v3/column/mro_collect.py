from __future__ import annotations

import logging
from typing import Dict

from .column_spec import ColumnSpec
from .io_spec import IOSpec as IO
from .storage_spec import StorageSpec as S

logger = logging.getLogger("uvicorn")


# Default inbound/outbound verbs for columns lacking an explicit ColumnSpec.
#
# Without this, plain SQLAlchemy ``Column`` definitions are omitted from the
# collected spec map, causing downstream components to treat their values as
# unknown.  By seeding such columns with a permissive IO spec we ensure they
# participate in canonical CRUD operations just like columns defined via
# ``acol``.
_DEFAULT_IO = IO(
    in_verbs=("create", "update", "replace"),
    out_verbs=("read", "list"),
    mutable_verbs=("create", "update", "replace"),
)


def mro_collect_columns(model: type) -> Dict[str, ColumnSpec]:
    """Collect ColumnSpecs declared on *model* and all mixins.

    Iterates across the model's MRO so that mixin-defined columns are included
    in the resulting mapping. Later definitions take precedence over earlier
    ones in the MRO.  Any table-backed columns lacking a spec are populated with
    a default ColumnSpec so they participate in opviews and schema generation.
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
        for col in table.columns:
            col_key = getattr(col, "key", None)
            col_name = getattr(col, "name", None)
            name = col_key or col_name
            if not name:
                continue
            out.setdefault(name, ColumnSpec(storage=S(), io=_DEFAULT_IO))

    logger.info("Collected %d columns for %s", len(out), model.__name__)
    return out


__all__ = ["mro_collect_columns"]
