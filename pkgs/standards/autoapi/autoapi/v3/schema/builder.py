# autoapi/v3/schema/builder.py
"""
Schema building for AutoAPI v3.

Builds verb-specific Pydantic models from SQLAlchemy ORM classes, with:
• Column.info["autoapi"] support (read_only, disable_on, no_update, write_only, default_factory, examples)
• Hybrid @hybrid_property *opt-in* via meta["hybrid"]
• Request-only virtual fields via __autoapi_request_extras__
• Response-only virtual fields via __autoapi_response_extras__
• A small cache keyed by (orm_cls, verb, include, exclude)
• A helper to strip fields from a parent schema class
"""

from __future__ import annotations

import logging
import uuid
from typing import (
    Any,
    Dict,
    Iterable,
    Literal,
    Mapping,
    Set,
    Tuple,
    Type,
    Union,
    get_type_hints,
)

from pydantic import BaseModel, ConfigDict, Field, create_model

from .utils import namely_model

try:
    # Optional: validate column meta (if available in your tree)
    from ..info_schema import check as _info_check  # type: ignore
except Exception:  # pragma: no cover

    def _info_check(meta: Mapping[str, Any], attr_name: str, model_name: str) -> None:
        return None  # no-op if v3.info_schema is absent


try:
    # Use SQLAlchemy's hybrid_property
    from sqlalchemy.ext.hybrid import hybrid_property  # type: ignore
except Exception:  # pragma: no cover

    class hybrid_property:  # minimal shim
        pass


try:
    # Pydantic v2 sentinel for "no default"
    from pydantic_core import PydanticUndefined  # type: ignore
except Exception:  # pragma: no cover

    class PydanticUndefinedClass:  # shim
        pass

    PydanticUndefined = PydanticUndefinedClass()  # type: ignore


from ..config.constants import (
    AUTOAPI_REQUEST_EXTRAS_ATTR,
    AUTOAPI_RESPONSE_EXTRAS_ATTR,
)

logger = logging.getLogger(__name__)

# ───────────────────────────────────────────────────────────────────────────────
# Types & cache
# ───────────────────────────────────────────────────────────────────────────────

_SchemaVerb = Union[
    # Canonical AutoAPI verbs
    Literal["create"],  # type: ignore[name-defined]
    Literal["read"],  # type: ignore[name-defined]
    Literal["update"],  # type: ignore[name-defined]
    Literal["replace"],  # type: ignore[name-defined]
    Literal["delete"],  # type: ignore[name-defined]
    Literal["list"],  # type: ignore[name-defined]
]

_SchemaCache: Dict[Tuple[type, str, frozenset, frozenset], Type[BaseModel]] = {}


# ───────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ───────────────────────────────────────────────────────────────────────────────


def _bool(x: Any) -> bool:
    try:
        return bool(x)
    except Exception:  # pragma: no cover
        return False


def _add_field(
    sink: Dict[str, Tuple[type, Field]],
    *,
    name: str,
    py_t: type | Any,
    field: Field | None = None,
) -> None:
    sink[name] = (py_t, field if field is not None else Field(None))


def _merge_request_extras(
    orm_cls: type,
    verb: str,
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
    buckets = getattr(orm_cls, AUTOAPI_REQUEST_EXTRAS_ATTR, None)
    if not buckets:
        return
    if verb not in {"create", "update", "replace", "delete"}:
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
            _add_field(fields, name=name, py_t=py_t, field=fld)
            logger.debug(
                "schema: added request-extra field %s (verb=%s, type=%r)",
                name,
                verb,
                py_t,
            )


def _merge_response_extras(
    orm_cls: type,
    verb: str,
    fields: Dict[str, Tuple[type, Field]],
    *,
    include: Set[str] | None,
    exclude: Set[str] | None,
) -> None:
    """Merge **response-only** virtual fields into the output schema."""
    buckets = getattr(orm_cls, AUTOAPI_RESPONSE_EXTRAS_ATTR, None)
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
            _add_field(fields, name=name, py_t=py_t, field=fld)
            logger.debug(
                "schema: added response-extra field %s (verb=%s, type=%r)",
                name,
                verb,
                py_t,
            )


def _python_type(col: Any) -> type | Any:
    try:
        return col.type.python_type
    except Exception:  # pragma: no cover
        return Any


def _is_required(col: Any, verb: str) -> bool:
    """
    Decide if a column should be required for this verb.
    - PK is required for update/replace/delete
    - otherwise, nullable or server/default determines optionality
    """
    if getattr(col, "primary_key", False) and verb in {"update", "replace", "delete"}:
        return True
    is_nullable = bool(getattr(col, "nullable", True))
    has_default = (getattr(col, "default", None) is not None) or (
        getattr(col, "server_default", None) is not None
    )
    return not is_nullable and not has_default


# ───────────────────────────────────────────────────────────────────────────────
# Public builders
# ───────────────────────────────────────────────────────────────────────────────


def _build_schema(
    orm_cls: type,
    *,
    name: str | None = None,
    include: Set[str] | None = None,
    exclude: Set[str] | None = None,
    verb: str = "create",
) -> Type[BaseModel]:
    """
    Build (and cache) a verb-specific Pydantic schema from *orm_cls*,
    ignoring relationships entirely. Columns come directly from __table__.columns
    (ColumnProperty only). Hybrids are handled in a separate pass.

    Supported metadata on columns or hybrids:
      • Column.info["autoapi"] with keys:
        - read_only   : bool | Iterable[str] | Mapping[str,bool]
        - write_only  : bool (hidden from read schemas)
        - disable_on  : Iterable[str] (verbs)
        - no_update   : legacy flag (treated like disable_on={"update","replace"})
        - default_factory, examples
      • Hybrid opt-in via meta["hybrid"] on the hybrid itself (.info["autoapi"])
      • __autoapi_request_extras__ / __autoapi_response_extras__ on the ORM class
    """
    cache_key = (orm_cls, verb, frozenset(include or ()), frozenset(exclude or ()))
    cached = _SchemaCache.get(cache_key)
    if cached is not None:
        logger.debug("schema: cache hit %s verb=%s", orm_cls.__name__, verb)
        return cached

    logger.debug(
        "schema: building %s verb=%s include=%s exclude=%s",
        orm_cls.__name__,
        verb,
        include,
        exclude,
    )
    fields: Dict[str, Tuple[type, Field]] = {}

    # ── PASS 1: table-backed columns only (avoid mapper relationships)
    table = getattr(orm_cls, "__table__", None)
    table_cols: Iterable[Any] = tuple(table.columns) if table is not None else ()
    specs = getattr(orm_cls, "__autoapi_cols__", {})

    for col in table_cols:
        attr_name = col.key or col.name

        if include and attr_name not in include:
            continue
        if exclude and attr_name in exclude:
            continue

        spec = specs.get(attr_name)
        io = getattr(spec, "io", None) if spec is not None else None
        if verb in {"create", "update", "replace"}:
            allowed_verbs = getattr(io, "in_verbs", ()) if io is not None else ()
            if verb not in set(allowed_verbs):
                continue

        # Column.info["autoapi"]
        meta_src = getattr(col, "info", {}) or {}
        meta = (meta_src.get("autoapi") if isinstance(meta_src, dict) else None) or {}
        _info_check(meta, attr_name, orm_cls.__name__)
        logger.debug("schema: processing column %s (verb=%s)", attr_name, verb)

        # Legacy flags
        if verb == "create" and getattr(meta_src, "get", lambda *_: None)("no_create"):
            continue
        if verb in {"update", "replace"} and getattr(meta_src, "get", lambda *_: None)(
            "no_update"
        ):
            continue

        # Disable on verb
        if verb in set(meta.get("disable_on", ()) or ()):
            continue

        # write_only → hide from read schemas
        if meta.get("write_only") and verb == "read":
            continue

        # read_only policies
        ro = meta.get("read_only")
        if isinstance(ro, Mapping):
            if _bool(ro.get(verb)):
                continue
        elif isinstance(ro, (set, list, tuple)):
            if verb in ro:
                continue
        elif ro and verb != "read":
            continue

        # Determine type and requiredness
        py_t = _python_type(col)
        required = _is_required(col, verb)

        # Field construction
        if "default_factory" in meta:
            fld = Field(default_factory=meta["default_factory"])
            required = False
        else:
            fld = Field(None if not required else ...)

        if "examples" in meta:
            fld = Field(fld.default, examples=meta["examples"])

        # Optional typing if nullable
        is_nullable = bool(getattr(col, "nullable", True))
        if is_nullable and py_t is not Any:
            py_t = Union[py_t, None]

        _add_field(fields, name=attr_name, py_t=py_t, field=fld)
        logger.debug(
            "schema: added field %s required=%s type=%r", attr_name, required, py_t
        )

    # ── PASS 2: @hybrid_property (opt-in via meta["hybrid"])
    for attr_name, attr in list(getattr(orm_cls, "__dict__", {}).items()):
        if not isinstance(attr, hybrid_property):
            continue

        if include and attr_name not in include:
            continue
        if exclude and attr_name in exclude:
            continue

        meta_src = getattr(attr, "info", {}) or {}
        meta = (meta_src.get("autoapi") if isinstance(meta_src, dict) else None) or {}

        # hybrids must explicitly opt-in
        if not meta.get("hybrid"):
            continue

        # Write-phase without setter is not usable
        if getattr(attr, "fset", None) is None and verb in {
            "create",
            "update",
            "replace",
        }:
            continue

        py_t = getattr(attr, "python_type", meta.get("py_type", Any))
        if "default_factory" in meta:
            fld = Field(default_factory=meta["default_factory"])
        else:
            fld = Field(None)

        if "examples" in meta:
            fld = Field(fld.default, examples=meta["examples"])

        _add_field(fields, name=attr_name, py_t=py_t, field=fld)
        logger.debug("schema: added hybrid field %s type=%r", attr_name, py_t)

    # ── PASS 3: request/response extras
    _merge_request_extras(orm_cls, verb, fields, include=include, exclude=exclude)
    _merge_response_extras(orm_cls, verb, fields, include=include, exclude=exclude)

    model_name = name or f"{orm_cls.__name__}{verb.capitalize()}"
    cfg = ConfigDict(from_attributes=True)

    schema_cls = create_model(model_name, __config__=cfg, **fields)  # type: ignore[arg-type]
    schema_cls.model_rebuild(force=True)
    schema_cls = namely_model(
        schema_cls,
        name=model_name,
        doc=f"AutoAPI v3 {orm_cls.__name__} {verb} schema",
    )
    _SchemaCache[cache_key] = schema_cls
    logger.debug("schema: created %s with %d fields", model_name, len(fields))
    return schema_cls


def _build_list_params(model: type) -> Type[BaseModel]:
    """
    Create a list/filter schema for the given model (forbid extra keys).
    Includes: skip>=0, limit>=10, plus nullable scalar filters for non-PK columns.
    """
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

    # Determine primary key name (first PK column)
    try:
        pk_name = next(iter(table.primary_key.columns)).name
    except Exception:
        pk_name = None

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
            spec_map = getattr(model, "__autoapi_colspecs__", None) or getattr(
                model, "__autoapi_cols__", {}
            )
            spec = spec_map.get(c.name) if isinstance(spec_map, Mapping) else None
            io = getattr(spec, "io", None)
            ops_raw = set(getattr(io, "filter_ops", ()) or [])
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


def _strip_parent_fields(base: Type[BaseModel], *, drop: Set[str]) -> Type[BaseModel]:
    """
    Return a shallow clone of *base* with selected fields removed.
    Preserves field types and defaults where possible.
    """
    assert issubclass(base, BaseModel), "base must be a Pydantic BaseModel subclass"
    hints = get_type_hints(base, include_extras=True)
    new_fields: Dict[str, Tuple[type, Any]] = {}

    for name, finfo in base.model_fields.items():  # type: ignore[attr-defined]
        if name in (drop or ()):
            continue
        typ = hints.get(name, Any)
        default = (
            finfo.default
            if getattr(finfo, "default", PydanticUndefined) is not PydanticUndefined
            else ...
        )
        new_fields[name] = (typ, default)

    clone = create_model(
        f"{base.__name__}Pruned",
        __config__=getattr(base, "model_config", None),
        **new_fields,
    )  # type: ignore[arg-type]
    clone.model_rebuild(force=True)
    return clone


__all__ = [
    "_build_schema",
    "_build_list_params",
    "_strip_parent_fields",
    "_merge_request_extras",
    "_merge_response_extras",
]
