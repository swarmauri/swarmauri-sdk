from __future__ import annotations

import logging
from typing import Dict

from .column_spec import ColumnSpec

logger = logging.getLogger("uvicorn")


def collect_columns(model: type) -> Dict[str, ColumnSpec]:
    """Gather ColumnSpecs declared on *model* and all mixins.

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
    logger.debug("Collected %d columns for %s", len(out), model.__name__)
    return out


__all__ = ["collect_columns"]
