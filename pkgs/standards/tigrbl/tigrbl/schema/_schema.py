# tigrbl/v3/schema/_schema.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Type

try:  # pragma: no cover
    from pydantic import BaseModel  # type: ignore
except Exception:  # pragma: no cover

    class BaseModel:  # minimal stub for typing only
        pass


from .types import SchemaKind


@dataclass(frozen=True, slots=True)
class Schema:
    """Concrete schema paired with its alias and kind."""

    model: Type[BaseModel]
    kind: SchemaKind = "out"
    alias: str | None = None


__all__ = ["Schema"]
