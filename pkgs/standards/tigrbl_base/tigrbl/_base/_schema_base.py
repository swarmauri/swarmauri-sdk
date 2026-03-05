from __future__ import annotations


class SchemaBase:
    """Shared schema helpers used by concrete schema wrappers."""

    @classmethod
    def collect(cls, model: type) -> dict[str, dict[str, type]]:
        from tigrbl_canon.tigrbl.mapping.collect_decorated_schemas import (
            collect_decorated_schemas,
        )

        return collect_decorated_schemas(model)


__all__ = ["SchemaBase"]
