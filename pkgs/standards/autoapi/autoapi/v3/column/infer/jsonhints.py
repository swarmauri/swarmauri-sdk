from __future__ import annotations

from typing import Optional

from .types import DataKind, PyTypeInfo, JsonHint, Email, Phone
from .planning import _nested_kind_from_py


def _json_hint(
    kind: DataKind, py: PyTypeInfo, *, max_length: Optional[int]
) -> JsonHint:
    if kind is DataKind.STRING:
        fmt = None
        if Email in py.annotated:
            fmt = "email"
        if Phone in py.annotated:
            fmt = "phone"
        return JsonHint(type="string", format=fmt, maxLength=max_length)
    if kind is DataKind.BYTES:
        return JsonHint(type="string", format="byte")
    if kind is DataKind.BOOL:
        return JsonHint(type="boolean")
    if kind is DataKind.INT or kind is DataKind.BIGINT:
        return JsonHint(type="integer")
    if kind is DataKind.FLOAT or kind is DataKind.DECIMAL:
        return JsonHint(type="number")
    if kind is DataKind.DATE:
        return JsonHint(type="string", format="date")
    if kind is DataKind.TIME:
        return JsonHint(type="string", format="time")
    if kind is DataKind.DATETIME:
        return JsonHint(type="string", format="date-time")
    if kind is DataKind.UUID:
        return JsonHint(type="string", format="uuid")
    if kind is DataKind.JSON:
        return JsonHint(type="object")
    if kind is DataKind.ENUM and py.enum_cls:
        return JsonHint(type="string", enum=[e.name for e in py.enum_cls])
    if kind is DataKind.ARRAY and py.array_item:
        elem_kind = _nested_kind_from_py(py.array_item)
        return JsonHint(
            type="array", items=_json_hint(elem_kind, py.array_item, max_length=None)
        )
    return JsonHint(type="string")
