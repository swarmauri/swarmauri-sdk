# pkgs/standards/tigrbl_core/tigrbl/_spec/schema_spec.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from tigrbl_core.schema.types import SchemaArg, SchemaKind, SchemaRef
from .serde import SerdeMixin


@dataclass(frozen=True, slots=True)
class SchemaSpec(SerdeMixin):
    """Declarative description of a schema for a model."""

    alias: str
    kind: SchemaKind = "out"
    for_: Optional[type] = None
    schema: SchemaArg | None = None


__all__ = ["SchemaSpec", "SchemaRef"]
