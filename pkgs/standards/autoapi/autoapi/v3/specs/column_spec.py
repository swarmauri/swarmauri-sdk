# column_spec.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Optional
from .storage_spec import StorageSpec as S
from .field_spec import FieldSpec as F
from .io_spec import IOSpec as IO


@dataclass(frozen=True)
class ColumnSpec:
    """
    - Persisted column: storage=S(...)
    - Virtual (wire-only) column: storage=None
    - default_factory: server-side scalar default IF not using IO.paired (runs when ABSENT)
    - read_producer: for virtuals on read/list (compute from ORM obj/ctx)
    """

    storage: Optional[S]  # None => virtual column (never persisted)
    field: F
    io: IO

    # Optional server default (non-paired). (ctx) -> value
    default_factory: Optional[Callable[[dict], object]] = None

    # Virtuals only: (obj, ctx) -> value for read/list responses
    read_producer: Optional[Callable[[object, dict], object]] = None
