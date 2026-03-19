# tigrbl/v3/schema/decorators.py
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

from pydantic import BaseModel, create_model

from tigrbl_core.config.constants import TIGRBL_SCHEMA_DECLS_ATTR

logger = logging.getLogger("uvicorn")


@dataclass(frozen=True)
class _SchemaDecl:
    alias: str  # name under model.schemas.<alias>
    kind: str  # "in" | "out"


def _coerce_schema_model(schema_cls: type, alias: str, kind: str) -> type:
    """Promote plain classes to Pydantic models for schema declarations."""
    del alias, kind
    if isinstance(schema_cls, type) and issubclass(schema_cls, BaseModel):
        return schema_cls

    annotations = dict(getattr(schema_cls, "__annotations__", {}) or {})
    fields: dict[str, tuple[Any, Any]] = {}
    for field_name, field_type in annotations.items():
        default = getattr(schema_cls, field_name, ...)
        fields[field_name] = (field_type, default)

    model_name = f"{schema_cls.__name__}Schema"
    return create_model(
        model_name, __base__=BaseModel, __module__=schema_cls.__module__, **fields
    )


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


def schema_ctx(*, alias: str, kind: str = "out", for_: Optional[type] = None):
    """Register a named schema for a model."""

    def deco(schema_cls: type):
        if not isinstance(schema_cls, type):
            logger.debug("schema_ctx applied to non-class %r", schema_cls)
            raise TypeError("@schema_ctx must decorate a class")

        normalized_schema = _coerce_schema_model(schema_cls, alias, kind)
        setattr(
            normalized_schema,
            "__tigrbl_schema_decl__",
            _SchemaDecl(alias=alias, kind=kind),
        )

        if for_ is not None:
            logger.debug(
                "Registering schema %s for model %s via decorator",
                normalized_schema,
                for_.__name__,
            )
            _register_schema_decl(for_, alias, kind, normalized_schema)

        logger.debug(
            "Attached schema decl to %s: alias=%s kind=%s",
            normalized_schema,
            alias,
            kind,
        )
        return normalized_schema

    return deco


__all__ = ["schema_ctx"]
