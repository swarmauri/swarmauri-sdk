from __future__ import annotations

from typing import Any, Dict, Optional

from .types import DataKind, PyTypeInfo, SATypePlan, InferenceError


def _plan_sa_type(
    kind: DataKind,
    py: PyTypeInfo,
    *,
    prefer_dialect: Optional[str],
    max_length: Optional[int],
    decimal_precision: Optional[int],
    decimal_scale: Optional[int],
) -> SATypePlan:
    d = prefer_dialect

    if kind is DataKind.STRING:
        if max_length and max_length > 0:
            return SATypePlan(
                name="String", args=(max_length,), kwargs={}, dialect=None
            )
        return SATypePlan(name="String", args=(), kwargs={}, dialect=None)

    if kind is DataKind.TEXT:
        return SATypePlan(name="Text", args=(), kwargs={}, dialect=None)

    if kind is DataKind.BYTES:
        return SATypePlan(name="LargeBinary", args=(), kwargs={}, dialect=None)

    if kind is DataKind.BOOL:
        return SATypePlan(name="Boolean", args=(), kwargs={}, dialect=None)

    if kind is DataKind.INT:
        return SATypePlan(name="Integer", args=(), kwargs={}, dialect=None)

    if kind is DataKind.BIGINT:
        return SATypePlan(name="BigInteger", args=(), kwargs={}, dialect=None)

    if kind is DataKind.FLOAT:
        return SATypePlan(name="Float", args=(), kwargs={}, dialect=None)

    if kind is DataKind.DECIMAL:
        kwargs: Dict[str, Any] = {}
        if decimal_precision is not None:
            kwargs["precision"] = decimal_precision
        if decimal_scale is not None:
            kwargs["scale"] = decimal_scale
        return SATypePlan(name="Numeric", args=(), kwargs=kwargs, dialect=None)

    if kind is DataKind.DATE:
        return SATypePlan(name="Date", args=(), kwargs={}, dialect=None)

    if kind is DataKind.TIME:
        return SATypePlan(name="Time", args=(), kwargs={"timezone": True}, dialect=None)

    if kind is DataKind.DATETIME:
        return SATypePlan(
            name="DateTime", args=(), kwargs={"timezone": True}, dialect=None
        )

    if kind is DataKind.UUID:
        if d == "postgresql":
            return SATypePlan(
                name="UUID", args=(), kwargs={"as_uuid": True}, dialect="postgresql"
            )
        return SATypePlan(name="String", args=(36,), kwargs={}, dialect=None)

    if kind is DataKind.JSON:
        if d == "postgresql":
            return SATypePlan(name="JSONB", args=(), kwargs={}, dialect="postgresql")
        return SATypePlan(name="JSON", args=(), kwargs={}, dialect=None)

    if kind is DataKind.ENUM:
        if not py.enum_cls:
            raise InferenceError("ENUM kind requires enum_cls in PyTypeInfo")
        return SATypePlan(
            name="Enum", args=(py.enum_cls,), kwargs={"native_enum": True}, dialect=None
        )

    if kind is DataKind.ARRAY:
        if not py.array_item:
            raise InferenceError("ARRAY kind requires array_item in PyTypeInfo")
        elem_plan = _plan_sa_type(
            _nested_kind_from_py(py.array_item),
            py.array_item,
            prefer_dialect=prefer_dialect,
            max_length=None,
            decimal_precision=None,
            decimal_scale=None,
        )
        if prefer_dialect == "postgresql":
            return SATypePlan(
                name="ARRAY",
                args=(elem_plan.name,),
                kwargs={},
                dialect="postgresql",
            )
        return SATypePlan(name="JSON", args=(), kwargs={}, dialect=None)

    raise InferenceError(f"Cannot plan SA type for kind={kind!r}")


def _nested_kind_from_py(nested_py: PyTypeInfo) -> DataKind:
    if nested_py.enum_cls is not None:
        return DataKind.ENUM
    b = nested_py.base
    import datetime as _dt
    import decimal as _dc
    import uuid as _uuid

    if b is str:
        return DataKind.STRING
    if b in (bytes, bytearray, memoryview):
        return DataKind.BYTES
    if b is bool:
        return DataKind.BOOL
    if b is int:
        return DataKind.INT
    if b is float:
        return DataKind.FLOAT
    if b is _dc.Decimal:
        return DataKind.DECIMAL
    if b is _dt.datetime:
        return DataKind.DATETIME
    if b is _dt.date:
        return DataKind.DATE
    if b is _dt.time:
        return DataKind.TIME
    if b is _uuid.UUID:
        return DataKind.UUID
    return DataKind.JSON
