# tigrbl/v3/schema/decorators.py
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Optional, get_type_hints, get_origin

from pydantic import BaseModel, create_model

from ..config.constants import TIGRBL_SCHEMA_DECLS_ATTR

logging.getLogger("uvicorn").setLevel(logging.DEBUG)
logger = logging.getLogger("uvicorn")


@dataclass(frozen=True)
class _SchemaDecl:
    alias: str  # name under model.schemas.<alias>
    kind: str  # "in" | "out"


def _register_schema_decl(
    target_model: type, alias: str, kind: str, schema_cls: type
) -> None:
    """Store schema declarations on the model for later binding."""
    logger.debug(
        "Registering schema decl for %s alias=%s kind=%s",
        target_model.__name__,
        alias,
        kind,
    )
    if kind not in ("in", "out"):
        logger.debug("Invalid kind '%s' for schema decl", kind)
        raise ValueError("schema_ctx(kind=...) must be 'in' or 'out'")
    mapping: Dict[str, Dict[str, type]] = (
        getattr(target_model, TIGRBL_SCHEMA_DECLS_ATTR, None) or {}
    )
    bucket = dict(mapping.get(alias, {}))
    bucket[kind] = schema_cls
    mapping[alias] = bucket
    setattr(target_model, TIGRBL_SCHEMA_DECLS_ATTR, mapping)
    logger.debug("Registered schema %s for alias '%s'", schema_cls, alias)


def _ensure_pydantic_model(schema_cls: type) -> type:
    """Promote plain classes to Pydantic models for schema declarations."""

    if isinstance(schema_cls, type) and issubclass(schema_cls, BaseModel):
        return schema_cls

    hints = get_type_hints(schema_cls, include_extras=True)
    fields: Dict[str, tuple[Any, Any]] = {}

    for name, hint in hints.items():
        if get_origin(hint) is ClassVar:
            continue
        default: Any = ...
        if name in schema_cls.__dict__:
            default = schema_cls.__dict__[name]
        fields[name] = (hint, default)

    model = create_model(schema_cls.__name__, __base__=BaseModel, **fields)
    model.__module__ = getattr(schema_cls, "__module__", model.__module__)
    model.__qualname__ = getattr(schema_cls, "__qualname__", model.__name__)
    model.__doc__ = getattr(schema_cls, "__doc__", model.__doc__)

    extra_attrs = {
        name: value
        for name, value in schema_cls.__dict__.items()
        if name not in fields
        and name not in {"__dict__", "__weakref__", "__annotations__"}
        and not name.startswith("__")
    }
    for name, value in extra_attrs.items():
        setattr(model, name, value)

    return model


def schema_ctx(*, alias: str, kind: str = "out", for_: Optional[type] = None):
    """Register a named schema for a model."""

    def deco(schema_cls: type):
        if not isinstance(schema_cls, type):
            logger.debug("schema_ctx applied to non-class %r", schema_cls)
            raise TypeError("@schema_ctx must decorate a class")
        schema_model = _ensure_pydantic_model(schema_cls)
        if for_ is not None:
            logger.debug(
                "Registering schema %s for model %s via decorator",
                schema_model,
                for_.__name__,
            )
            _register_schema_decl(for_, alias, kind, schema_model)
        setattr(
            schema_model,
            "__tigrbl_schema_decl__",
            _SchemaDecl(alias=alias, kind=kind),
        )
        logger.debug(
            "Attached schema decl to %s: alias=%s kind=%s", schema_model, alias, kind
        )
        return schema_model

    return deco


__all__ = ["schema_ctx"]
