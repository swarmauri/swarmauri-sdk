# autoapi/v3/specs/shortcuts.py

from __future__ import annotations

from typing import Any, Callable, Optional

from .column_spec import ColumnSpec
from .field_spec import FieldSpec as F
from .io_spec import IOSpec as IO
from .storage_spec import StorageSpec as S


__all__ = ["acol", "vcol", "F", "IO", "S", "ColumnSpec"]


def acol(
    *,
    storage: S | None = None,
    field: F | None = None,
    io: IO | None = None,
    default_factory: Optional[Callable[[dict], Any]] = None,
    read_producer: Optional[Callable[[object, dict], Any]] = None,
    spec: ColumnSpec | None = None,
) -> ColumnSpec:
    """Return a ColumnSpec descriptor for declarative models."""
    if spec is not None:
        if any(
            x is not None for x in (storage, field, io, default_factory, read_producer)
        ):
            raise ValueError("Provide either spec or individual components, not both.")
    if spec is None:
        if read_producer is not None and storage is not None:
            raise ValueError(
                "read_producer is only valid for virtual (storage=None) columns."
            )
        spec = ColumnSpec(
            storage=storage,
            field=field,
            io=io,
            default_factory=default_factory,
            read_producer=read_producer,
        )
    return spec


def vcol(
    *,
    field: F | None = None,
    io: IO | None = None,
    default_factory: Optional[Callable[[dict], Any]] = None,
    producer: Optional[Callable[[object, dict], Any]] = None,
    read_producer: Optional[Callable[[object, dict], Any]] = None,
    spec: ColumnSpec | None = None,
) -> ColumnSpec:
    """Convenience for wire-only virtual columns."""
    if spec is not None:
        if any(
            x is not None for x in (field, io, default_factory, producer, read_producer)
        ):
            raise ValueError("Provide either spec or individual components, not both.")
        return spec
    if producer is not None and read_producer is not None:
        raise ValueError("Provide only one of producer= or read_producer=, not both.")
    rp = read_producer or producer
    return ColumnSpec(
        storage=None,
        field=field,
        io=io,
        default_factory=default_factory,
        read_producer=rp,
    )
