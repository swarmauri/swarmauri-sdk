# tigrbl/v3/schema/collect.py
from __future__ import annotations

import inspect
import logging
from functools import lru_cache
from typing import Dict

from ..config.constants import TIGRBL_SCHEMA_DECLS_ATTR

from .decorators import _SchemaDecl
from pydantic import BaseModel, create_model

logger = logging.getLogger("uvicorn")


@lru_cache(maxsize=None)
def collect_decorated_schemas(model: type) -> Dict[str, Dict[str, type]]:
    """Gather schema declarations for ``model`` across its MRO."""
    logger.info("Collecting decorated schemas for %s", model.__name__)
    out: Dict[str, Dict[str, type]] = {}

    def _promote_schema(schema_cls: type) -> type:
        if issubclass(schema_cls, BaseModel):
            return schema_cls
        annotations = getattr(schema_cls, "__annotations__", {}) or {}
        fields = {}
        for name, anno in annotations.items():
            default = getattr(schema_cls, name, ...)
            fields[name] = (anno, default)
        promoted = create_model(  # type: ignore[call-arg]
            schema_cls.__name__,
            __base__=BaseModel,
            **fields,
        )
        promoted.__module__ = schema_cls.__module__
        promoted.__qualname__ = schema_cls.__qualname__
        promoted.__doc__ = schema_cls.__doc__
        return promoted

    # Explicit registrations (MRO-merged)
    for base in reversed(model.__mro__):
        mapping: Dict[str, Dict[str, type]] = (
            getattr(base, TIGRBL_SCHEMA_DECLS_ATTR, {}) or {}
        )
        if mapping:
            logger.debug(
                "Found explicit schema mapping on %s: %s", base.__name__, mapping
            )
        for alias, kinds in mapping.items():
            bucket = out.setdefault(alias, {})
            bucket.update(
                {
                    kind: _promote_schema(schema)
                    for kind, schema in (kinds or {}).items()
                }
            )

    # Nested classes with __tigrbl_schema_decl__
    for base in reversed(model.__mro__):
        for name, obj in base.__dict__.items():
            if not inspect.isclass(obj):
                logger.debug("Skipping non-class attribute %s.%s", base.__name__, name)
                continue
            decl: _SchemaDecl | None = getattr(obj, "__tigrbl_schema_decl__", None)
            if not decl:
                logger.debug(
                    "Class %s.%s has no schema declaration", base.__name__, name
                )
                continue
            bucket = out.setdefault(decl.alias, {})
            bucket[decl.kind] = _promote_schema(obj)

    logger.debug("Collected schema aliases: %s", list(out.keys()))
    return out


__all__ = ["collect_decorated_schemas"]
