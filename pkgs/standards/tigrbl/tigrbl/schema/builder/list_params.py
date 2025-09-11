"""Schema builders for list parameter models."""

from __future__ import annotations

import logging
import uuid
from typing import Any, Type

from pydantic import BaseModel, ConfigDict, Field, create_model

from ..utils import namely_model
from ...column.mro_collect import mro_collect_columns

logger = logging.getLogger(__name__)


def _build_list_params(model: type) -> Type[BaseModel]:
    """Create a list/filter schema for the given model."""
    tab = model.__name__
    logger.debug("schema: build_list_params for %s", tab)

    base = dict(
        skip=(int | None, Field(None, ge=0)),
        limit=(int | None, Field(None, ge=10)),
        sort=(str | list[str] | None, Field(None)),
    )
    _scalars = {str, int, float, bool, bytes, uuid.UUID}
    cols: dict[str, tuple[type, Field]] = {}

    table = getattr(model, "__table__", None)
    if table is None or not getattr(table, "columns", None):
        # No table info; return a minimal pager schema
        schema = create_model(
            f"{tab}ListParams", __config__=ConfigDict(extra="forbid"), **base
        )  # type: ignore[arg-type]
        schema = namely_model(
            schema,
            name=f"{tab}ListParams",
            doc=f"List parameters for {tab}",
        )
        logger.debug(
            "schema: build_list_params generated %s (no columns)", schema.__name__
        )
        return schema

    pk_name = None
    for c in table.columns:
        if getattr(c, "primary_key", False):
            pk_name = c.name
            break

    _canon = {
        "eq": "eq",
        "=": "eq",
        "==": "eq",
        "ne": "ne",
        "!=": "ne",
        "<>": "ne",
        "lt": "lt",
        "<": "lt",
        "gt": "gt",
        ">": "gt",
        "lte": "lte",
        "le": "lte",
        "<=": "lte",
        "gte": "gte",
        "ge": "gte",
        ">=": "gte",
        "like": "like",
        "not_like": "not_like",
        "ilike": "ilike",
        "not_ilike": "not_ilike",
        "in": "in",
        "not_in": "not_in",
    }

    for c in table.columns:
        if pk_name and c.name == pk_name:
            continue
        py_t = getattr(c.type, "python_type", Any)
        if py_t in _scalars:
            spec_map = mro_collect_columns(model)
            spec = spec_map.get(c.name)
            io = getattr(spec, "io", None)
            ops_raw = set(getattr(io, "filter_ops", ()) or [])
            if not ops_raw:
                # Allow basic equality filtering by default on scalar columns
                ops_raw = {"eq"}
            ops = {_canon.get(op, op) for op in ops_raw}
            if "eq" in ops:
                cols[c.name] = (py_t | None, Field(None))
                logger.debug("schema: list filter add %s type=%r", c.name, py_t)
            for op in ops:
                if op == "eq":
                    continue
                fname = f"{c.name}__{op}"
                cols[fname] = (py_t | None, Field(None))
                logger.debug(
                    "schema: list filter add %s op=%s type=%r", c.name, op, py_t
                )

    schema = create_model(
        f"{tab}ListParams",
        __config__=ConfigDict(extra="forbid"),
        **base,  # type: ignore[arg-type]
        **cols,  # type: ignore[arg-type]
    )
    schema = namely_model(
        schema,
        name=f"{tab}ListParams",
        doc=f"List parameters for {tab}",
    )
    logger.debug("schema: build_list_params generated %s", schema.__name__)
    return schema


__all__ = ["_build_list_params"]
