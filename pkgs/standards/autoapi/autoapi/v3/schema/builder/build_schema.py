"""Core schema builder logic for AutoAPI v3."""

from __future__ import annotations

import logging
import warnings
from typing import Any, Dict, Iterable, Mapping, Set, Tuple, Type, Union

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, create_model

from ..utils import namely_model
from ...column.mro_collect import mro_collect_columns
from .cache import _SchemaCache
from .compat import _info_check, hybrid_property
from .extras import _merge_request_extras, _merge_response_extras
from .helpers import _add_field, _bool, _is_required, _python_type

logger = logging.getLogger(__name__)


def _build_schema(
    orm_cls: type,
    *,
    name: str | None = None,
    include: Set[str] | None = None,
    exclude: Set[str] | None = None,
    verb: str = "create",
) -> Type[BaseModel]:
    """Build (and cache) a verb-specific Pydantic schema for *orm_cls*."""
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
    specs: Dict[str, Any] = mro_collect_columns(orm_cls)

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
                if allowed_verbs is not None:
                    if not allowed_verbs and not getattr(io, "out_verbs", None):
                        pass  # treat default IOSpec with no verbs as allow-all
                    elif verb not in set(allowed_verbs):
                        continue

        # Column.info["autoapi"]
        meta_src = getattr(col, "info", {}) or {}
        if isinstance(meta_src, Mapping) and "autoapi" in meta_src:
            warnings.warn(
                "col.info['autoapi'] is deprecated and support will be removed;"
                " behavior is no longer guaranteed for col.info['autoapi'] based"
                " column configuration.",
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
                "col.info['autoapi'] is deprecated and support will be removed;"
                " behavior is no longer guaranteed for col.info['autoapi'] based"
                " column configuration.",
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
    cfg_kwargs = {"from_attributes": True}
    if verb in {"create", "update", "replace"}:
        cfg_kwargs["extra"] = "forbid"
    cfg = ConfigDict(**cfg_kwargs)

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


__all__ = ["_build_schema"]
