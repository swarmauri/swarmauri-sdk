# autoapi/v3/schema/collect.py
from __future__ import annotations

import inspect
import logging
from functools import lru_cache
from typing import Dict

from ..config.constants import AUTOAPI_SCHEMA_DECLS_ATTR

from .decorators import _SchemaDecl

logging.getLogger("uvicorn").setLevel(logging.DEBUG)
logger = logging.getLogger("uvicorn")


@lru_cache(maxsize=None)
def collect_decorated_schemas(model: type) -> Dict[str, Dict[str, type]]:
    """Gather schema declarations for ``model`` across its MRO."""
    logger.info("Collecting decorated schemas for %s", model.__name__)
    out: Dict[str, Dict[str, type]] = {}

    # Explicit registrations (MRO-merged)
    for base in reversed(model.__mro__):
        mapping: Dict[str, Dict[str, type]] = (
            getattr(base, AUTOAPI_SCHEMA_DECLS_ATTR, {}) or {}
        )
        if mapping:
            logger.debug(
                "Found explicit schema mapping on %s: %s", base.__name__, mapping
            )
        for alias, kinds in mapping.items():
            bucket = out.setdefault(alias, {})
            bucket.update(kinds or {})

    # Nested classes with __autoapi_schema_decl__
    for base in reversed(model.__mro__):
        for name in dir(base):
            obj = getattr(base, name, None)
            if not inspect.isclass(obj):
                logger.debug("Skipping non-class attribute %s.%s", base.__name__, name)
                continue
            decl: _SchemaDecl | None = getattr(obj, "__autoapi_schema_decl__", None)
            if not decl:
                logger.debug(
                    "Class %s.%s has no schema declaration", base.__name__, name
                )
                continue
            bucket = out.setdefault(decl.alias, {})
            bucket[decl.kind] = obj

    logger.debug("Collected schema aliases: %s", list(out.keys()))
    return out


__all__ = ["collect_decorated_schemas"]
