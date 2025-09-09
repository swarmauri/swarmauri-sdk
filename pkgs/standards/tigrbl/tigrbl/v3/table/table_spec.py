# tigrbl/tigrbl/v3/table/table_spec.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Sequence

from ..engine.engine_spec import EngineCfg
from ..response.types import ResponseSpec


@dataclass
class TableSpec:
    """
    Declarative enrichments for an ORM class (model == table).
    This does not construct an instance; it decorates/produces a class.
    """

    model: Any  # ORM class
    engine: Optional[EngineCfg] = None

    # NEW
    ops: Sequence[Any] = field(default_factory=tuple)  # OpSpec or shorthands
    columns: Sequence[Any] = field(default_factory=tuple)  # ColumnSpec or shorthands
    schemas: Sequence[Any] = field(default_factory=tuple)
    hooks: Sequence[Callable[..., Any]] = field(default_factory=tuple)
    security_deps: Sequence[Callable[..., Any]] = field(default_factory=tuple)
    deps: Sequence[Callable[..., Any]] = field(default_factory=tuple)

    response: Optional[ResponseSpec] = None
