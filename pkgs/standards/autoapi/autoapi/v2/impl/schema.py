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


def _merge_response_extras(
    orm_cls: type,
    verb: _SchemaVerb,
    fields: Dict[str, Tuple[type, Field]],
    *,
    include: Set[str] | None,
    exclude: Set[str] | None,
) -> None:
    """Merge **response-only** virtual fields into the output schema."""

    buckets = getattr(orm_cls, "__autoapi_response_extras__", None)
    if not buckets:
        return

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
            print(f"Added response-extra field {name} type={py_t} verb={verb}")


def _build_schema(
    orm_cls: type,
    *,
    name: str | None = None,
    include: Set[str] | None = None,
    exclude: Set[str] | None = None,
    verb: _SchemaVerb = "create",
) -> Type[BaseModel]:
    """
    Build (and cache) a verb-specific Pydantic schema from *orm_cls*,
    ignoring relationships entirely. Columns come from mapper.column_attrs
    (ColumnProperty only). Hybrids are handled in a separate pass.

    Keeps support for:
      • Column.info["autoapi"] (read_only, write_only, disable_on, no_update, …)
      • @hybrid_property opt-in via meta["hybrid"]
      • __autoapi_request_extras__ / __autoapi_response_extras__
    """
    cache_key = (orm_cls, verb, frozenset(include or ()), frozenset(exclude or ()))
    if cache_key in _SchemaCache:
        print(f"_schema cache hit for {orm_cls} verb={verb}")
        return _SchemaCache[cache_key]
    print(
        f"_schema generating model for {orm_cls} verb={verb} include={include} exclude={exclude}"
    )

    fields: Dict[str, Tuple[type, Field]] = {}

    # ── PASS 1: table-backed columns only (NO mapper; avoids relationship config)
    table = getattr(orm_cls, "__table__", None)
    if table is None:
        # Abstract / unmapped — still allow extras & hybrids to populate a schema
        table_cols = []
    else:
        table_cols = list(table.columns)

    for col in table_cols:
        attr_name = col.key or col.name

        if include and attr_name not in include:
            continue
        if exclude and attr_name in exclude:
            continue

        meta_src = getattr(col, "info", {}) or {}
        meta = (meta_src.get("autoapi") if isinstance(meta_src, dict) else None) or {}
        _info_check(meta, attr_name, orm_cls.__name__)
        print(f"Processing column attribute {attr_name}")

        # Legacy flags (kept for back-compat)
        if verb == "create" and getattr(col.info, "get", lambda *_: None)("no_create"):
            continue
        if verb in {"update", "replace"} and getattr(col.info, "get", lambda *_: None)(
            "no_update"
        ):
            continue

        if verb in set(meta.get("disable_on", ()) or ()):
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

        # Type + requiredness
        try:
            py_t = col.type.python_type
        except Exception:
            py_t = Any

        is_nullable = bool(getattr(col, "nullable", True))
        has_default = (getattr(col, "default", None) is not None) or (
            getattr(col, "server_default", None) is not None
        )
        required = not is_nullable and not has_default

        # Ensure PK required on write/delete verbs that need identification
        if getattr(col, "primary_key", False) and verb in {
            "update",
            "replace",
            "delete",
        }:
            required = True

        # Field construction
        if "default_factory" in meta:
            fld = Field(default_factory=meta["default_factory"])
            required = False
        else:
            fld = Field(None if not required else ...)

        if "examples" in meta:
            fld = Field(fld.default, examples=meta["examples"])

        if is_nullable and py_t is not Any:
            py_t = Union[py_t, None]

        fields[attr_name] = (py_t, fld)
        print(f"Added field {attr_name} type={py_t} required={required}")

    # ── PASS 2: @hybrid_property (opt-in via meta["hybrid"])
    for attr in (
        v for v in orm_cls.__dict__.values() if isinstance(v, hybrid_property)
    ):
        attr_name = (
            getattr(attr, "__name__", None) or getattr(attr, "key", None) or "<hybrid>"
        )
        if include and attr_name not in include:
            continue
        if exclude and attr_name in exclude:
            continue

        # Allow attaching meta to the hybrid itself (e.g., attr.info = {"autoapi": {...}})
        meta_src = getattr(attr, "info", {}) or {}
        meta = (meta_src.get("autoapi") if isinstance(meta_src, dict) else None) or {}

        # hybrids must explicitly opt-in
        if not meta.get("hybrid"):
            continue

        # Write-phase without setter is not usable
        if attr.fset is None and verb in {"create", "update", "replace"}:
            continue

        py_t = getattr(attr, "python_type", meta.get("py_type", Any))
        if "default_factory" in meta:
            fld = Field(default_factory=meta["default_factory"])
        else:
            fld = Field(None)

        if "examples" in meta:
            fld = Field(fld.default, examples=meta["examples"])

        fields[attr_name] = (py_t, fld)
        print(f"Added hybrid field {attr_name} type={py_t}")

    # Request/response extras
    # (read/list are OUTPUT schemas – request extras are ignored there)
    _merge_request_extras(orm_cls, verb, fields, include=include, exclude=exclude)
    _merge_response_extras(orm_cls, verb, fields, include=include, exclude=exclude)

    model_name = name or f"{orm_cls.__name__}{verb.capitalize()}"
    cfg = ConfigDict(from_attributes=True)

    schema_cls = create_model(model_name, __config__=cfg, **fields)
    schema_cls.model_rebuild(force=True)
    _SchemaCache[cache_key] = schema_cls
    print(f"Created schema {model_name} with fields {list(fields)}")
    return schema_cls


def _build_list_params(model: type) -> Type[BaseModel]:
    """
    Create a list/filter schema for the given model.
    """
    tab = model.__name__
    print(f"_build_list_params for {tab}")
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
    print(f"_build_list_params generated {schema.__name__}")
    return schema
