"""Core schema builders for AutoAPI v3."""

from __future__ import annotations

import inspect
import logging
import uuid
import warnings
from typing import (
    Any,
    Dict,
    Iterable,
    Mapping,
    Set,
    Tuple,
    Type,
    Union,
    get_args,
    get_origin,
    get_type_hints,
    List,
)

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, create_model

from ..utils import namely_model

try:
    # Optional: validate column meta (if available in your tree)
    from ...info_schema import check as _info_check  # type: ignore
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


from .cache import _SchemaCache
from .helpers import _bool, _add_field, _python_type, _is_required
from .extras import _merge_request_extras, _merge_response_extras

logger = logging.getLogger(__name__)


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
    (ColumnProperty only).

    Supported metadata on columns:
      • Column.info["autoapi"] with keys:
        - read_only   : bool | Iterable[str] | Mapping[str,bool]
        - write_only  : bool (hidden from read schemas)
        - disable_on  : Iterable[str] (verbs)
        - no_update   : legacy flag (treated like disable_on={"update","replace"})
        - default_factory, examples
      • __autoapi_request_extras__ / __autoapi_response_extras__ on the ORM class
    """
    cache_key = (
        orm_cls,
        verb,
        frozenset(include or ()),
        frozenset(exclude or ()),
        name,
    )
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
    specs: Dict[str, Any] = {}
    specs.update(getattr(orm_cls, "__autoapi_colspecs__", {}))
    specs.update(getattr(orm_cls, "__autoapi_cols__", {}))

    for col in table_cols:
        attr_name = col.key or col.name

        if include and attr_name not in include:
            continue
        if exclude and attr_name in exclude:
            continue

        spec = specs.get(attr_name)
        io = getattr(spec, "io", None) if spec is not None else None
        if verb in {"create", "update", "replace"}:
            """Determine if the column participates in inbound verbs.

            When a ColumnSpec is present it may explicitly restrict the verbs a
            field accepts via ``io.in_verbs``.  Previous behaviour treated the
            absence of this specification as "deny all", which caused models
            without explicit ColumnSpec declarations to generate empty request
            schemas.  Here we interpret a missing ``io`` or ``in_verbs`` as
            allowing all verbs, only filtering when the spec explicitly lists
            them.
            """

            if getattr(col, "primary_key", False) and verb in {
                "update",
                "replace",
                "delete",
            }:
                # Always expose the PK for mutating operations even when the
                # ColumnSpec omits inbound verbs. The identifier is required so
                # consumers can target the correct row.
                pass
            else:
                allowed_verbs = (
                    getattr(io, "in_verbs", None) if io is not None else None
                )
                if allowed_verbs is not None and verb not in set(allowed_verbs):
                    continue

        # Column.info["autoapi"]
        meta_src = getattr(col, "info", {}) or {}
        if isinstance(meta_src, Mapping) and "autoapi" in meta_src:
            warnings.warn(
                "col.info['autoapi'] is deprecated and support will be removed; behavior is no longer guaranteed for col.info['autoapi'] based column configuration.",
                DeprecationWarning,
                stacklevel=5,
            )
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

        # Field construction (collect kwargs then create Field once)
        field_kwargs: Dict[str, Any] = {}
        if "default_factory" in meta:
            field_kwargs["default_factory"] = meta["default_factory"]
            required = False
        else:
            field_kwargs["default"] = None if not required else ...

        if "examples" in meta:
            field_kwargs["examples"] = meta["examples"]

        # IOSpec aliases → Pydantic validation/serialization aliases
        alias_in = getattr(io, "alias_in", None) if io is not None else None
        alias_out = getattr(io, "alias_out", None) if io is not None else None
        if alias_in:
            field_kwargs["validation_alias"] = AliasChoices(alias_in, attr_name)
        if alias_out:
            field_kwargs["serialization_alias"] = alias_out

        fld = Field(**field_kwargs)

        # Optional typing if nullable
        is_nullable = bool(getattr(col, "nullable", True))
        if is_nullable and py_t is not Any:
            py_t = Union[py_t, None]

        # Apply alias mappings for IO specs so that generated Pydantic models
        # accept both the canonical field name and any configured alias. This
        # ensures request payloads can use ``alias_in`` and response models use
        # ``alias_out`` while still normalizing to the canonical attribute name
        # internally.
        if io is not None:
            if verb in {"read", "list"}:
                alias = getattr(io, "alias_out", None)
            else:
                alias = getattr(io, "alias_in", None)
            if alias:
                fld.alias = alias
                fld.serialization_alias = alias
                fld.validation_alias = AliasChoices(attr_name, alias)

        _add_field(fields, name=attr_name, py_t=py_t, field=fld)
        logger.debug(
            "schema: added field %s required=%s type=%r", attr_name, required, py_t
        )

    # ── PASS 1b: virtual columns declared via ColumnSpec --------------------
    for attr_name, spec in specs.items():
        if getattr(spec, "storage", None) is not None:
            continue  # real columns handled above
        if include and attr_name not in include:
            continue
        if exclude and attr_name in exclude:
            continue

        io = getattr(spec, "io", None)
        allowed_verbs = set(getattr(io, "in_verbs", ()) or ()) | set(
            getattr(io, "out_verbs", ()) or ()
        )
        if allowed_verbs and verb not in allowed_verbs:
            continue

        fs = getattr(spec, "field", None)
        py_t = getattr(fs, "py_type", Any) if fs is not None else Any
        required = bool(fs and verb in getattr(fs, "required_in", ()))
        allow_null = bool(fs and verb in getattr(fs, "allow_null_in", ()))
        field_kwargs: Dict[str, Any] = dict(getattr(fs, "constraints", {}) or {})

        default_factory = getattr(spec, "default_factory", None)
        if default_factory and verb in set(getattr(spec.io, "in_verbs", []) or []):
            field_kwargs["default_factory"] = default_factory
            required = False
        else:
            field_kwargs["default"] = None if not required else ...

        fld = Field(**field_kwargs)

        if allow_null and py_t is not Any:
            py_t = Union[py_t, None]

        _add_field(fields, name=attr_name, py_t=py_t, field=fld)
        logger.debug(
            "schema: added virtual field %s required=%s type=%r",
            attr_name,
            required,
            py_t,
        )

    # ── PASS 2: reject @hybrid_property usage
    for attr_name, attr in list(getattr(orm_cls, "__dict__", {}).items()):
        if not isinstance(attr, hybrid_property):
            continue

        meta_src = getattr(attr, "info", {}) or {}
        if isinstance(meta_src, Mapping) and "autoapi" in meta_src:
            warnings.warn(
                "col.info['autoapi'] is deprecated and support will be removed; behavior is no longer guaranteed for col.info['autoapi'] based column configuration.",
                DeprecationWarning,
                stacklevel=5,
            )
        meta = (meta_src.get("autoapi") if isinstance(meta_src, dict) else None) or {}

        if meta.get("hybrid"):
            raise ValueError(
                f"{orm_cls.__name__}.{attr_name}: hybrid_property is not supported"
            )

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
            spec_map = getattr(model, "__autoapi_colspecs__", None) or getattr(
                model, "__autoapi_cols__", {}
            )
            spec = spec_map.get(c.name) if isinstance(spec_map, Mapping) else None
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


def _strip_parent_fields(base: Type[BaseModel], *, drop: Set[str]) -> Type[BaseModel]:
    """
    Return a shallow clone of *base* with selected fields removed.
    Preserves field types and defaults where possible.
    """
    assert issubclass(base, BaseModel), "base must be a Pydantic BaseModel subclass"

    # RootModel[Union[Model, List[Model]]] – unwrap inner model so we can strip
    # identifiers and return the cleaned schema directly.
    if len(getattr(base, "model_fields", {})) == 1 and "root" in base.model_fields:
        root_ann = base.model_fields["root"].annotation
        if get_origin(root_ann) is Union:
            item_type = None
            for arg in get_args(root_ann):
                origin = get_origin(arg)
                if inspect.isclass(arg) and issubclass(arg, BaseModel):
                    item_type = arg
                    break
                if origin in (list, List):
                    sub = get_args(arg)[0]
                    if inspect.isclass(sub) and issubclass(sub, BaseModel):
                        item_type = sub
                        break
            if item_type is not None:
                return _strip_parent_fields(item_type, drop=drop)

    hints = get_type_hints(base, include_extras=True)
    new_fields: Dict[str, Tuple[type, Any]] = {}

    for name, finfo in base.model_fields.items():  # type: ignore[attr-defined]
        if name in (drop or ()):  # pragma: no branch
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
]
