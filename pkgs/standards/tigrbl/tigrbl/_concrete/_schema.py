# tigrbl/v3/schema/_schema.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Type

try:  # pragma: no cover
    from pydantic import BaseModel  # type: ignore
except Exception:  # pragma: no cover

    class BaseModel:  # minimal stub for typing only
        pass


from ..schema.types import SchemaKind


@dataclass(frozen=True, slots=True)
class Schema:
    """Concrete schema paired with its alias and kind."""

    model: Type[BaseModel]
    kind: SchemaKind = "out"
    alias: str | None = None

    @classmethod
    def collect(cls, model: type) -> dict[str, dict[str, type]]:
        from ..schema.collect import collect_decorated_schemas

        return collect_decorated_schemas(model)


__all__ = ["Schema"]
