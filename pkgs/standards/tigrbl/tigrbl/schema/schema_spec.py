# tigrbl/v3/schema/schema_spec.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .types import SchemaArg, SchemaKind


@dataclass(frozen=True, slots=True)
class SchemaSpec:
    """Declarative description of a schema for a model."""

    alias: str
    kind: SchemaKind = "out"
    for_: Optional[type] = None
    schema: SchemaArg | None = None


__all__ = ["SchemaSpec"]
