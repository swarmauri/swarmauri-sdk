# autoapi/v3/schema/decorators.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from ..config.constants import AUTOAPI_SCHEMA_DECLS_ATTR


@dataclass(frozen=True)
class _SchemaDecl:
    alias: str  # name under model.schemas.<alias>
    kind: str  # "in" | "out"


def _register_schema_decl(
    target_model: type, alias: str, kind: str, schema_cls: type
) -> None:
    """Store schema declarations on the model for later binding."""
    if kind not in ("in", "out"):
        raise ValueError("schema_ctx(kind=...) must be 'in' or 'out'")
    mapping: Dict[str, Dict[str, type]] = (
        getattr(target_model, AUTOAPI_SCHEMA_DECLS_ATTR, None) or {}
    )
    bucket = dict(mapping.get(alias, {}))
    bucket[kind] = schema_cls
    mapping[alias] = bucket
    setattr(target_model, AUTOAPI_SCHEMA_DECLS_ATTR, mapping)


def schema_ctx(*, alias: str, kind: str = "out", for_: Optional[type] = None):
    """Register a named schema for a model."""

    def deco(schema_cls: type):
        if not isinstance(schema_cls, type):
            raise TypeError("@schema_ctx must decorate a class")
        if for_ is not None:
            _register_schema_decl(for_, alias, kind, schema_cls)
        setattr(
            schema_cls, "__autoapi_schema_decl__", _SchemaDecl(alias=alias, kind=kind)
        )
        return schema_cls

    return deco


__all__ = ["schema_ctx"]
