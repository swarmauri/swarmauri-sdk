# autoapi/v3/specs/shortcuts.py

from __future__ import annotations

from typing import Callable, Optional, Any

from .column_spec import ColumnSpec
from .field_spec import FieldSpec as F
from .io_spec import IOSpec as IO
from .storage_spec import StorageSpec as S


__all__ = [
    "acol",
    "vcol",
    "F",
    "IO",
    "S",
]


def _ensure_field(field: F | None) -> F:
    """Provide a default FieldSpec when omitted. Authors may rely on type inference."""
    return field if field is not None else F()  # F.py_type may be inferred later


def _ensure_io(io: IO | None) -> IO:
    """Provide a default IOSpec when omitted (no in/out by default)."""
    return io if io is not None else IO()


def acol(
    *,
    storage: S | None,
    field: F | None = None,
    io: IO | None = None,
    default_factory: Optional[Callable[[dict], Any]] = None,
    read_producer: Optional[Callable[[object, dict], Any]] = None,
) -> ColumnSpec:
    """
    Unified ColumnSpec constructor used in models.

    - Persisted column: pass a StorageSpec instance in `storage`.
    - Virtual (wire-only) column: pass `storage=None` (or prefer vcol(...)).

    `default_factory` is a server-side scalar default used only when the input is ABSENT
    (non-paired path). `read_producer` is only meaningful for virtuals, used to compute
    the read/list value from the hydrated ORM object.
    """
    # Guard: read_producer only applies to virtuals
    if read_producer is not None and storage is not None:
        raise ValueError(
            "read_producer is only valid for virtual (storage=None) columns."
        )

    return ColumnSpec(
        storage=storage,
        field=_ensure_field(field),
        io=_ensure_io(io),
        default_factory=default_factory,
        read_producer=read_producer,
    )


def vcol(
    *,
    field: F | None = None,
    io: IO | None = None,
    default_factory: Optional[Callable[[dict], Any]] = None,
    producer: Optional[Callable[[object, dict], Any]] = None,
    read_producer: Optional[Callable[[object, dict], Any]] = None,
) -> ColumnSpec:
    """
    Convenience for wire-only virtual columns.

    Exactly equivalent to:
        ColumnSpec(storage=None, field=..., io=..., default_factory=..., read_producer=...)

    `default_factory(ctx)` supplies a value on write verbs when the input is ABSENT.
    `producer(obj, ctx)` (alias: `read_producer`) supplies a value on read/list.
    """
    if producer is not None and read_producer is not None:
        raise ValueError("Provide only one of producer= or read_producer=, not both.")
    rp = read_producer or producer

    return ColumnSpec(
        storage=None,
        field=_ensure_field(field),
        io=_ensure_io(io),
        default_factory=default_factory,
        read_producer=rp,
    )
