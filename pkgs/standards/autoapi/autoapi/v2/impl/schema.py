"""
autoapi/v2/schema.py  –  Schema building functionality for AutoAPI.

This module contains the schema generation logic that creates Pydantic models
from SQLAlchemy ORM classes with verb-specific configurations.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, Set, Tuple, Type, Union

from pydantic import BaseModel, ConfigDict, Field, create_model
from sqlalchemy import inspect as _sa_inspect

from ..info_schema import check as _info_check
from ..types import _SchemaVerb, hybrid_property

# ────────────────────────────────────────────────────────────────────────────
_SchemaCache: Dict[Tuple[type, str, frozenset, frozenset], Type] = {}


def _schema(
    orm_cls: type,
    *,
    name: str | None = None,
    include: Set[str] | None = None,
    exclude: Set[str] | None = None,
    verb: _SchemaVerb = "create",
) -> Type[BaseModel]:
    """
    Build (and cache) a verb-specific Pydantic schema from *orm_cls*.
    Supports rich Column.info["autoapi"] metadata.

    Args:
        orm_cls: SQLAlchemy ORM class to generate schema from
        name: Optional custom name for the generated schema
        include: Set of field names to include (if None, include all eligible fields)
        exclude: Set of field names to exclude
        verb: Schema verb ("create", "read", "update", "replace", "delete", "list")

    Returns:
        Generated Pydantic model class
    """
    cache_key = (orm_cls, verb, frozenset(include or ()), frozenset(exclude or ()))
    if cache_key in _SchemaCache:
        return _SchemaCache[cache_key]

    mapper = _sa_inspect(orm_cls)
    fields: Dict[str, Tuple[type, Field]] = {}

    attrs = list(mapper.attrs) + [
        v for v in orm_cls.__dict__.values() if isinstance(v, hybrid_property)
    ]
    for attr in attrs:
        is_hybrid = isinstance(attr, hybrid_property)
        is_col_attr = not is_hybrid and hasattr(attr, "columns")
        if not is_hybrid and not is_col_attr:
            continue

        col = attr.columns[0] if is_col_attr and attr.columns else None
        meta_src = (
            col.info
            if col is not None and hasattr(col, "info")
            else getattr(attr, "info", {})
        )
        meta = meta_src.get("autoapi", {}) or {}

        attr_name = getattr(attr, "key", getattr(attr, "__name__", None))
        _info_check(meta, attr_name, orm_cls.__name__)

        # hybrids must opt-in
        if is_hybrid and not meta.get("hybrid"):
            continue

        # legacy flags
        if verb == "create" and col is not None and col.info.get("no_create"):
            continue
        if (
            verb in {"update", "replace"}
            and col is not None
            and col.info.get("no_update")
        ):
            continue

        if verb in meta.get("disable_on", []):
            continue
        if meta.get("write_only") and verb == "read":
            continue

        ro = meta.get("read_only")
        if isinstance(ro, dict):
            if ro.get(verb):
                continue
        elif isinstance(ro, (set, list, tuple)):
            if verb in ro:
                continue
        elif ro and verb != "read":
            continue
        if is_hybrid and attr.fset is None and verb in {"create", "update", "replace"}:
            continue
        if include and attr_name not in include:
            continue
        if exclude and attr_name in exclude:
            continue

        # type / required / default
        if col is not None:
            try:
                py_t = col.type.python_type
            except Exception:
                py_t = Any
            is_nullable = bool(getattr(col, "nullable", True))
            has_default = getattr(col, "default", None) is not None
            required = not is_nullable and not has_default
            if col.primary_key and verb in {"update", "replace"}:
                required = True
        else:  # hybrid
            py_t = getattr(attr, "python_type", meta.get("py_type", Any))
            required = False

        if "default_factory" in meta:
            fld = Field(default_factory=meta["default_factory"])
            required = False
        else:
            fld = Field(None if not required else ...)

        if "examples" in meta:
            fld = Field(fld.default, examples=meta["examples"])

        # Make nullable fields Optional for proper Pydantic validation
        if col is not None and is_nullable and py_t is not Any:
            py_t = Union[py_t, None]

        fields[attr_name] = (py_t, fld)

    model_name = name or f"{orm_cls.__name__}{verb.capitalize()}"
    cfg = ConfigDict(from_attributes=True)

    schema_cls = create_model(
        model_name,
        __config__=cfg,
        **fields,
    )
    schema_cls.model_rebuild(force=True)
    _SchemaCache[cache_key] = schema_cls
    return schema_cls


def create_list_schema(model: type) -> Type[BaseModel]:
    """
    Create a list/filter schema for the given model.

    Args:
        model: SQLAlchemy ORM model

    Returns:
        Pydantic schema for list filtering parameters
    """
    tab = "".join(w.title() for w in model.__tablename__.split("_"))
    base = dict(
        skip=(int | None, Field(None, ge=0)),
        limit=(int | None, Field(None, ge=10)),
    )
    _scalars = {str, int, float, bool, bytes, uuid.UUID}
    cols: dict[str, tuple[type, Field]] = {}

    pk = next(iter(model.__table__.primary_key.columns)).name

    for c in model.__table__.columns:
        if c.name == pk:
            continue
        py_t = getattr(c.type, "python_type", Any)
        if py_t in _scalars:
            cols[c.name] = (py_t | None, Field(None))

    return create_model(
        f"{tab}ListParams", __config__=ConfigDict(extra="forbid"), **base, **cols
    )
