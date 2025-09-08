"""Core schema builder logic for AutoAPI v3."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, Set, Tuple, Type, Union

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, create_model

from ..utils import namely_model
from ...column.mro_collect import mro_collect_columns
from .cache import _SchemaCache
from .compat import hybrid_property
from .extras import _merge_request_extras, _merge_response_extras
from .helpers import _add_field, _is_required, _python_type

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

        if verb in {"read", "list"}:
            allowed_verbs = getattr(io, "out_verbs", None) if io is not None else None
            if allowed_verbs is not None and verb not in set(allowed_verbs):
                continue
        elif getattr(col, "primary_key", False) and verb in {
            "update",
            "replace",
            "delete",
        }:
            pass
        else:
            allowed_verbs = getattr(io, "in_verbs", None) if io is not None else None
            if allowed_verbs is not None and verb not in set(allowed_verbs):
                continue

        logger.debug("schema: processing column %s (verb=%s)", attr_name, verb)

        fs = getattr(spec, "field", None)
        py_t = getattr(fs, "py_type", Any)
        if py_t is Any:
            py_t = _python_type(col)

        required = _is_required(col, verb)
        if fs is not None and verb in getattr(fs, "required_in", ()):  # noqa: SIM108
            required = True

        field_kwargs: Dict[str, Any] = dict(getattr(fs, "constraints", {}) or {})

        default_factory = getattr(spec, "default_factory", None)
        if default_factory and verb in set(getattr(io, "in_verbs", ()) or ()):
            field_kwargs["default_factory"] = default_factory
            required = False
        else:
            field_kwargs["default"] = None if not required else ...

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
        field_kwargs: Dict[str, Any] = dict(getattr(fs, "constraints", {}) or {})

        default_factory = getattr(spec, "default_factory", None)
        if default_factory and verb in set(getattr(spec.io, "in_verbs", []) or []):
            field_kwargs["default_factory"] = default_factory
            required = False
        else:
            field_kwargs["default"] = None if not required else ...

        fld = Field(**field_kwargs)

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
