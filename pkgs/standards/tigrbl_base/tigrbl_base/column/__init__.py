from __future__ import annotations

from typing import Any, Callable, Optional

from tigrbl_base._base import ColumnBase
from tigrbl_core._spec.column_spec import ColumnSpec
from tigrbl_core._spec.field_spec import FieldSpec as F
from tigrbl_core._spec.io_spec import IOSpec as IO
from tigrbl_core._spec.storage_spec import StorageSpec as S

from .infer import (
    DataKind,
    Email,
    InferenceError,
    Inferred,
    JsonHint,
    Phone,
    PyTypeInfo,
    SATypePlan,
    UnsupportedType,
    infer,
)


def makeColumn(
    *,
    storage: S | None = None,
    field: F | None = None,
    io: IO | None = None,
    default_factory: Optional[Callable[[dict], Any]] = None,
    read_producer: Optional[Callable[[object, dict], Any]] = None,
    spec: ColumnSpec | None = None,
    **kw: Any,
) -> ColumnBase:
    """Return a :class:`ColumnBase` descriptor for declarative models."""
    if spec is not None and any(
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
    return ColumnBase(spec=spec, **kw)


def makeVirtualColumn(
    *,
    field: F | None = None,
    io: IO | None = None,
    default_factory: Optional[Callable[[dict], Any]] = None,
    producer: Optional[Callable[[object, dict], Any]] = None,
    read_producer: Optional[Callable[[object, dict], Any]] = None,
    spec: ColumnSpec | None = None,
    **kw: Any,
) -> ColumnBase:
    """Convenience helper for wire-only virtual columns."""
    if spec is not None and any(x is not None for x in (field, io, default_factory)):
        raise ValueError("Provide either spec or individual components, not both.")
    if producer is not None and read_producer is not None:
        raise ValueError("Provide only one of producer= or read_producer=, not both.")

    rp = read_producer or producer
    if spec is not None:
        if rp is not None:
            spec = ColumnSpec(
                storage=spec.storage,
                field=spec.field,
                io=spec.io,
                default_factory=spec.default_factory,
                read_producer=rp,
            )
        return ColumnBase(spec=spec, **kw)

    return ColumnBase(
        spec=ColumnSpec(
            storage=None,
            field=field,
            io=io,
            default_factory=default_factory,
            read_producer=rp,
        ),
        **kw,
    )


def is_virtual(spec: ColumnSpec) -> bool:
    return spec.storage is None


acol = makeColumn
vcol = makeVirtualColumn

__all__ = [
    "ColumnSpec",
    "ColumnBase",
    "F",
    "IO",
    "S",
    "makeColumn",
    "makeVirtualColumn",
    "acol",
    "vcol",
    "is_virtual",
    "infer",
    "Email",
    "Phone",
    "DataKind",
    "PyTypeInfo",
    "SATypePlan",
    "JsonHint",
    "Inferred",
    "InferenceError",
    "UnsupportedType",
]
