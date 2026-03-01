from __future__ import annotations

import logging
from functools import lru_cache
from typing import Dict

from .._spec.column_spec import ColumnSpec
from .._spec.io_spec import IOSpec as IO
from .._spec.storage_spec import StorageSpec as S

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


def _model_label(model: object) -> str:
    return str(
        getattr(model, "__name__", None)
        or getattr(model, "name", None)
        or type(model).__name__
    )


@lru_cache(maxsize=None)
def mro_collect_columns(
    model: object, *, _cache_bust: int | None = None
) -> Dict[str, ColumnSpec]:
    """Collect ColumnSpecs declared on *model* and all mixins.

    Iterates across the model's MRO so that mixin-defined columns are included
    in the resulting mapping. Later definitions take precedence over earlier
    ones in the MRO.  Any table-backed columns lacking a spec are populated with
    a default ColumnSpec so they participate in opviews and schema generation.
    """
    logger.info("Collecting columns for %s", _model_label(model))
    out: Dict[str, ColumnSpec] = {}
    mro = getattr(model, "__mro__", ()) or ()
    for base in reversed(mro):
        mapping = getattr(base, "__tigrbl_colspecs__", None)
        if isinstance(mapping, dict):
            out.update(mapping)
        mapping = getattr(base, "__tigrbl_cols__", None)
        if isinstance(mapping, dict):
            out.update(mapping)

    cols = None
    table = getattr(model, "__table__", None)
    if table is not None:
        cols = getattr(table, "columns", None)
    elif hasattr(model, "columns"):
        cols = getattr(model, "columns", None)

    if cols is not None:
        for col in cols:
            name = getattr(col, "key", None) or getattr(col, "name", None)
            if not isinstance(name, str):
                continue
            out.setdefault(name, ColumnSpec(storage=S(), io=_DEFAULT_IO))

    logger.info("Collected %d columns for %s", len(out), _model_label(model))
    return out


__all__ = ["mro_collect_columns"]
