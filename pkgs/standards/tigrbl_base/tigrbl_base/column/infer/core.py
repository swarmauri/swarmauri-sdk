from __future__ import annotations

from typing import Any, Dict, Optional, get_origin

from .jsonhints import _json_hint
from .planning import _plan_sa_type
from .types import DataKind, Inferred, PyTypeInfo
from .utils import _array_item, _is_enum, _strip_annotated, _strip_optional


def infer(
    annotation: Any,
    *,
    prefer_dialect: Optional[str] = "postgresql",
    max_length: Optional[int] = None,
    decimal_precision: Optional[int] = None,
    decimal_scale: Optional[int] = None,
) -> Inferred:
    """Bind-time inference from Python annotation to DataKind and hints."""
    base, is_opt = _strip_optional(annotation)
    base, meta = _strip_annotated(base)

    enum_cls = _is_enum(base)
    item_tp = _array_item(base)

    array_item_info: Optional[PyTypeInfo] = None
    if item_tp is not None:
        nested = infer(
            item_tp,
            prefer_dialect=prefer_dialect,
            max_length=max_length,
            decimal_precision=decimal_precision,
            decimal_scale=decimal_scale,
        )
        array_item_info = nested.py

    py_info = PyTypeInfo(
        base=base,
        is_optional=is_opt,
        enum_cls=enum_cls,
        array_item=array_item_info,
        annotated=meta,
    )

    import datetime as _dt
    import decimal as _dc
    import uuid as _uuid

    origin = get_origin(base)

    if enum_cls is not None:
        kind = DataKind.ENUM
    elif item_tp is not None:
        kind = DataKind.ARRAY
    elif base is str:
        kind = DataKind.STRING
    elif base in (bytes, bytearray, memoryview):
        kind = DataKind.BYTES
    elif base is bool:
        kind = DataKind.BOOL
    elif base is int:
        kind = DataKind.INT
    elif base is float:
        kind = DataKind.FLOAT
    elif base is _dc.Decimal:
        kind = DataKind.DECIMAL
    elif base is _dt.datetime:
        kind = DataKind.DATETIME
    elif base is _dt.date:
        kind = DataKind.DATE
    elif base is _dt.time:
        kind = DataKind.TIME
    elif base is _uuid.UUID:
        kind = DataKind.UUID
    else:
        if origin in (dict, Dict):
            kind = DataKind.JSON
        else:
            kind = DataKind.JSON

    sa = _plan_sa_type(
        kind,
        py_info,
        prefer_dialect=prefer_dialect,
        max_length=max_length,
        decimal_precision=decimal_precision,
        decimal_scale=decimal_scale,
    )

    jh = _json_hint(kind, py_info, max_length=max_length)
    return Inferred(kind=kind, py=py_info, sa=sa, json=jh, nullable=is_opt)
