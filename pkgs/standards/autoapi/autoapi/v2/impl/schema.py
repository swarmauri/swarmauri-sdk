"""
autoapi/v2/impl/schema.py  –  Schema building functionality for AutoAPI.

Builds verb-specific Pydantic models from SQLAlchemy ORM classes, with:
• Column.info["autoapi"] support (read_only, disable_on, no_update, …)
• Hybrid @hybrid_property opt-in via meta["hybrid"]
• Request-only virtual fields via __autoapi_request_extras__ on the ORM class
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


def _merge_request_extras(
    orm_cls: type,
    verb: _SchemaVerb,
    fields: Dict[str, Tuple[type, Field]],
    *,
    include: Set[str] | None,
    exclude: Set[str] | None,
) -> None:
    """
    Merge **request-only** virtual fields into the input schema.

    The ORM may declare:
        __autoapi_request_extras__ = {
            "*": { "github_pat": (str | None, Field(default=None, exclude=True)) },
            "create": {...}, "update": {...}, "delete": {...}, "replace": {...}
        }

    Notes:
    • Applied only to request verbs (create/update/replace/delete)
    • Respects include/exclude sets
    • Field(...) is used as-is; if only a type is provided, defaults to Field(None)
    • Recommend Field(exclude=True) for secrets so they drop from .model_dump()
    """
    buckets = getattr(orm_cls, "__autoapi_request_extras__", None)
    if not buckets:
        return

    # read/list are OUTPUT schemas – do not merge extras there
    if verb not in {"create", "update", "replace", "delete"}:
        return

    # verb-specific extras override/extend wildcard
    for bucket in (buckets.get("*", {}), buckets.get(verb, {})):
        for name, spec in (bucket or {}).items():
            if include and name not in include:
                continue
            if exclude and name in exclude:
                continue

            if isinstance(spec, tuple) and len(spec) == 2:
                py_t, fld = spec
            else:
                py_t, fld = (spec or Any), Field(None)

            fields[name] = (py_t, fld)
            print(f"Added request-extra field {name} type={py_t} verb={verb}")


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
    Supports rich Column.info["autoapi"] metadata and request-only extras.

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
        print(f"_schema cache hit for {orm_cls} verb={verb}")
        return _SchemaCache[cache_key]
    print(
        f"_schema generating model for {orm_cls} verb={verb} include={include} exclude={exclude}"
    )

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
        print(f"Processing attribute {attr_name}")

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
        print(f"Added field {attr_name} type={py_t} required={required}")

    # Merge request-only extras (create/update/replace/delete only)
    _merge_request_extras(orm_cls, verb, fields, include=include, exclude=exclude)

    model_name = name or f"{orm_cls.__name__}{verb.capitalize()}"
    cfg = ConfigDict(from_attributes=True)

    schema_cls = create_model(
        model_name,
        __config__=cfg,
        **fields,
    )
    schema_cls.model_rebuild(force=True)
    _SchemaCache[cache_key] = schema_cls
    print(f"Created schema {model_name} with fields {list(fields)}")
    return schema_cls


def create_list_schema(model: type) -> Type[BaseModel]:
    """
    Create a list/filter schema for the given model.
    """
    tab = "".join(w.title() for w in model.__tablename__.split("_"))
    print(f"create_list_schema for {tab}")
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
            print(f"Added list filter field {c.name} type={py_t}")

    schema = create_model(
        f"{tab}ListParams", __config__=ConfigDict(extra="forbid"), **base, **cols
    )
    print(f"create_list_schema generated {schema.__name__}")
    return schema
