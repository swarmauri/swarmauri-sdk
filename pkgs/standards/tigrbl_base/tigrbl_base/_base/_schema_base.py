from __future__ import annotations

import inspect
from types import SimpleNamespace

from tigrbl_core.config.constants import TIGRBL_SCHEMA_DECLS_ATTR


class SchemaBase:
    """Shared schema helpers used by concrete schema wrappers."""

    @classmethod
    def collect(cls, model: type) -> dict[str, dict[str, type]]:
        """Collect schema declarations from explicit mappings and decorator metadata."""

        collected: dict[str, dict[str, type]] = {}

        explicit = getattr(model, TIGRBL_SCHEMA_DECLS_ATTR, None) or {}
        if isinstance(explicit, dict):
            for alias, kinds in explicit.items():
                if isinstance(kinds, dict):
                    collected[alias] = dict(kinds)

        schemas = getattr(model, "schemas", None)
        if isinstance(schemas, dict):
            for alias, kinds in schemas.items():
                if isinstance(kinds, dict):
                    collected[alias] = {**collected.get(alias, {}), **kinds}

        for _, obj in model.__dict__.items():
            if not inspect.isclass(obj):
                continue
            decl = getattr(obj, "__tigrbl_schema_decl__", None)
            if decl is None:
                continue
            bucket = collected.setdefault(decl.alias, {})
            bucket[decl.kind] = obj

        if isinstance(schemas, SimpleNamespace):
            for alias, ns in vars(schemas).items():
                if not isinstance(ns, SimpleNamespace):
                    continue
                bucket = collected.setdefault(alias, {})
                if getattr(ns, "in_", None) is not None:
                    bucket.setdefault("in", ns.in_)
                if getattr(ns, "out", None) is not None:
                    bucket.setdefault("out", ns.out)

        return collected


__all__ = ["SchemaBase"]
