from __future__ import annotations


class SchemaBase:
    """Shared schema helpers used by concrete schema wrappers."""

    @classmethod
    def collect(cls, model: type) -> dict[str, dict[str, type]]:
        """Collect schema declarations from model-local attributes only."""

        schemas = getattr(model, "schemas", None)
        if isinstance(schemas, dict):
            return dict(schemas)
        return {}


__all__ = ["SchemaBase"]
