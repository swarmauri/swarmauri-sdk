from __future__ import annotations

from typing import Any, Callable, Optional

from ._column import Column
from .column_spec import ColumnSpec
from .field_spec import FieldSpec as F
from .io_spec import IOSpec as IO
from .storage_spec import StorageSpec as S

__all__ = [
    "makeColumn",
    "makeVirtualColumn",
    "acol",
    "vcol",
    "F",
    "IO",
    "S",
    "ColumnSpec",
    "Column",
]


def makeColumn(
    *,
    storage: S | None = None,
    field: F | None = None,
    io: IO | None = None,
    default_factory: Optional[Callable[[dict], Any]] = None,
    read_producer: Optional[Callable[[object, dict], Any]] = None,
    spec: ColumnSpec | None = None,
    **kw: Any,
) -> Column:
    """Return a :class:`Column` descriptor for declarative models."""
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
    return Column(spec=spec, **kw)


def makeVirtualColumn(
    *,
    field: F | None = None,
    io: IO | None = None,
    default_factory: Optional[Callable[[dict], Any]] = None,
    producer: Optional[Callable[[object, dict], Any]] = None,
    read_producer: Optional[Callable[[object, dict], Any]] = None,
    spec: ColumnSpec | None = None,
    **kw: Any,
) -> Column:
    """Convenience for wire-only virtual columns."""
    if spec is not None:
        if any(x is not None for x in (field, io, default_factory)):
            raise ValueError("Provide either spec or individual components, not both.")
        if producer is not None and read_producer is not None:
            raise ValueError(
                "Provide only one of producer= or read_producer=, not both."
            )
        rp = read_producer or producer
        if rp is not None:
            spec = ColumnSpec(
                storage=spec.storage,
                field=spec.field,
                io=spec.io,
                default_factory=spec.default_factory,
                read_producer=rp,
            )
        return Column(spec=spec, **kw)
    if producer is not None and read_producer is not None:
        raise ValueError("Provide only one of producer= or read_producer=, not both.")
    rp = read_producer or producer
    return Column(
        spec=ColumnSpec(
            storage=None,
            field=field,
            io=io,
            default_factory=default_factory,
            read_producer=rp,
        ),
        **kw,
    )


# Convenience aliases retained for backward compatibility
acol = makeColumn
vcol = makeVirtualColumn
