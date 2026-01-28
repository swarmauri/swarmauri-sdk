# tigrbl/v3/schema/decorators.py
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, Optional

from ..config.constants import TIGRBL_SCHEMA_DECLS_ATTR

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


def schema_ctx(*, alias: str, kind: str = "out", for_: Optional[type] = None):
    """Register a named schema for a model."""

    def deco(schema_cls: type):
        if not isinstance(schema_cls, type):
            logger.debug("schema_ctx applied to non-class %r", schema_cls)
            raise TypeError("@schema_ctx must decorate a class")
        if for_ is not None:
            logger.debug(
                "Registering schema %s for model %s via decorator",
                schema_cls,
                for_.__name__,
            )
            _register_schema_decl(for_, alias, kind, schema_cls)
        setattr(
            schema_cls, "__tigrbl_schema_decl__", _SchemaDecl(alias=alias, kind=kind)
        )
        logger.debug(
            "Attached schema decl to %s: alias=%s kind=%s", schema_cls, alias, kind
        )
        return schema_cls

    return deco


__all__ = ["schema_ctx"]
