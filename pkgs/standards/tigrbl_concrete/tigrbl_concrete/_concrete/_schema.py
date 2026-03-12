# tigrbl/_concrete/_schema.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Type

try:  # pragma: no cover
    from pydantic import BaseModel  # type: ignore
except Exception:  # pragma: no cover

    class BaseModel:  # minimal stub for typing only
        pass


from tigrbl_base._base import SchemaBase
from tigrbl_core._spec.schema_spec import SchemaKind


@dataclass(frozen=True, slots=True)
class Schema(SchemaBase):
    """Concrete schema paired with its alias and kind."""

    model: Type[BaseModel]
    kind: SchemaKind = "out"
    alias: str | None = None


__all__ = ["Schema"]
