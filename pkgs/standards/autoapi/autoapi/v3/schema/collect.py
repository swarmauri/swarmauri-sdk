# autoapi/v3/schema/collect.py
from __future__ import annotations

import inspect
from typing import Dict

from ..config.constants import AUTOAPI_SCHEMA_DECLS_ATTR

from .decorators import _SchemaDecl


def collect_decorated_schemas(model: type) -> Dict[str, Dict[str, type]]:
    """Gather schema declarations for ``model`` across its MRO."""
    out: Dict[str, Dict[str, type]] = {}

    # Explicit registrations (MRO-merged)
    for base in reversed(model.__mro__):
        mapping: Dict[str, Dict[str, type]] = (
            getattr(base, AUTOAPI_SCHEMA_DECLS_ATTR, {}) or {}
        )
        for alias, kinds in mapping.items():
            bucket = out.setdefault(alias, {})
            bucket.update(kinds or {})

    # Nested classes with __autoapi_schema_decl__
    for base in reversed(model.__mro__):
        for name in dir(base):
            obj = getattr(base, name, None)
            if not inspect.isclass(obj):
                continue
            decl: _SchemaDecl | None = getattr(obj, "__autoapi_schema_decl__", None)
            if not decl:
                continue
            bucket = out.setdefault(decl.alias, {})
            bucket[decl.kind] = obj

    return out


__all__ = ["collect_decorated_schemas"]
