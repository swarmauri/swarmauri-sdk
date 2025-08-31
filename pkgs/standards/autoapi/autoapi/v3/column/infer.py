# autoapi/v3/specs/infer.py
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
    Type,
    Union,
    get_args,
    get_origin,
    Annotated,
)

# ──────────────────────────────────────────────────────────────────────────────
# Public markers (wire/adapters provide validation/normalization at runtime)
# ──────────────────────────────────────────────────────────────────────────────


class Email:  # marker for Annotated[str, Email]
    """Marker indicating email string semantics."""


class Phone:  # marker for Annotated[str, Phone]  (E.164)
    """Marker indicating E.164 phone string semantics."""


# ──────────────────────────────────────────────────────────────────────────────
# Portable data-kind (DB- and adapter-agnostic)
# ──────────────────────────────────────────────────────────────────────────────


class DataKind(str, Enum):
    STRING = "string"
    TEXT = "text"
    BYTES = "bytes"
    BOOL = "bool"
    INT = "int"
    BIGINT = "bigint"
    FLOAT = "float"
    DECIMAL = "decimal"
    DATE = "date"
    TIME = "time"
    DATETIME = "datetime"
    UUID = "uuid"
    JSON = "json"
    ENUM = "enum"
    ARRAY = "array"


# ──────────────────────────────────────────────────────────────────────────────
# Structured outputs
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class PyTypeInfo:
    """Normalized info about the Python-side type annotation."""

    base: Any
    is_optional: bool = False
    enum_cls: Optional[Type[Enum]] = None
    array_item: Optional["PyTypeInfo"] = None
    annotated: Tuple[Any, ...] = ()  # Annotated metadata (Email/Phone/etc.)


@dataclass(frozen=True)
class SATypePlan:
    """
    A declarative plan for constructing an SA column type downstream.
    We avoid importing SQLAlchemy here; downstream creates the actual object.
    """

    name: str  # e.g., "UUID", "String", "JSONB", "Enum", "ARRAY"
    args: Tuple[Any, ...]  # positional args (e.g., (enum_cls,))
    kwargs: Dict[str, Any]  # keyword args (e.g., {"as_uuid": True})
    dialect: Optional[str] = None  # e.g., "postgresql" for JSONB/UUID/ARRAY


@dataclass(frozen=True)
class JsonHint:
    """Minimal JSON Schema-ish hints for docs."""

    type: str
    format: Optional[str] = None
    maxLength: Optional[int] = None
    enum: Optional[List[str]] = None
    items: Optional["JsonHint"] = None


@dataclass(frozen=True)
class Inferred:
    """Primary product of inference."""

    kind: DataKind
    py: PyTypeInfo
    sa: SATypePlan
    json: JsonHint
    nullable: bool


# ──────────────────────────────────────────────────────────────────────────────
# Errors
# ──────────────────────────────────────────────────────────────────────────────


class InferenceError(ValueError): ...


class UnsupportedType(InferenceError): ...


# ──────────────────────────────────────────────────────────────────────────────
# Utilities: unwrap Optional / Annotated, arrays, enums
# ──────────────────────────────────────────────────────────────────────────────


def _strip_optional(tp: Any) -> Tuple[Any, bool]:
    """Return (inner_type, is_optional) for Optional[T] / Union[T, None]."""
    origin = get_origin(tp)
    if origin is Union:
        args = tuple(a for a in get_args(tp))
        if len(args) == 2 and type(None) in args:
            inner = args[0] if args[1] is type(None) else args[1]
            return inner, True
    return tp, False


def _strip_annotated(tp: Any) -> Tuple[Any, Tuple[Any, ...]]:
    """Return (base, metadata) for Annotated[base, *meta]; otherwise (tp, ())."""
    origin = get_origin(tp)
    if origin is Annotated:
        args = get_args(tp)
        if len(args) >= 1:
            base, meta = args[0], tuple(args[1:])
            return base, meta
    return tp, ()


def _array_item(tp: Any) -> Optional[Any]:
    origin = get_origin(tp)
    if origin in (list, List, tuple, Tuple, set, frozenset):
        args = get_args(tp)
        if not args:
            return Any
        # for Tuple[T, ...] -> treat as array of T
        if origin in (tuple, Tuple) and len(args) == 2 and args[1] is Ellipsis:
            return args[0]
        # generic list[T] or set[T]
        if len(args) == 1:
            return args[0]
        # mixed tuples -> fall back to Any
        return Any
    return None


def _is_enum(tp: Any) -> Optional[Type[Enum]]:
    try:
        if isinstance(tp, type) and issubclass(tp, Enum):
            return tp
    except Exception:
        pass
    return None


# ──────────────────────────────────────────────────────────────────────────────
# Core inference
# ──────────────────────────────────────────────────────────────────────────────


def infer(
    annotation: Any,
    *,
    prefer_dialect: Optional[str] = "postgresql",
    # string sizing & decimals are optional, can also be supplied via FieldSpec
    max_length: Optional[int] = None,
    decimal_precision: Optional[int] = None,
    decimal_scale: Optional[int] = None,
) -> Inferred:
    """
    Bind-time inference from Python annotation to (DataKind, SATypePlan, JsonHint).

    Rules (brief-aligned):
    - Optional[...] → nullable=True (storage S.nullable)
    - Annotated[str, Email] / Annotated[str, Phone] → DataKind.STRING with format
      hint for docs (wire handles actual validation/normalization).
    - Enum → DataKind.ENUM with SA Enum plan
    - list[T]/set[T]/Tuple[T, ...] → DataKind.ARRAY with item inference
    - uuid.UUID → UUID
    - datetime/date/time → as named
    - bytes/bytearray → BYTES
    - int/float/Decimal → INT/FLOAT/DECIMAL (precision/scale optional)
    - dict / untyped mapping → JSON
    - fallback for str: STRING (String(length) if provided; else Text vs String
      decision is left to storage layer—default here is String)

    No SQLAlchemy is imported here; we only describe the type.
    """
    # 1) Unwrap Optional and Annotated
    base, is_opt = _strip_optional(annotation)
    base, meta = _strip_annotated(base)

    # 2) Enum?
    enum_cls = _is_enum(base)

    # 3) Array?
    item_tp = _array_item(base)

    # 4) Build PyTypeInfo (possibly recursively for arrays)
    array_item_info: Optional[PyTypeInfo] = None
    if item_tp is not None:
        # Recurse with a shallow call (arrays cannot be Optional at item-level by annotation rules here)
        nested = infer(
            item_tp,
            prefer_dialect=prefer_dialect,
            max_length=max_length,
            decimal_precision=decimal_precision,
            decimal_scale=decimal_scale,
        )
        array_item_info = nested.py
        # We will collapse vendor plans below; json hint will also reference nested.json

    py_info = PyTypeInfo(
        base=base,
        is_optional=is_opt,
        enum_cls=enum_cls,
        array_item=array_item_info,
        annotated=meta,
    )

    # 5) Determine DataKind
    import datetime as _dt
    import decimal as _dc
    import uuid as _uuid

    origin = get_origin(base)
    kind: DataKind

    if enum_cls is not None:
        kind = DataKind.ENUM
    elif item_tp is not None:
        kind = DataKind.ARRAY
    elif base in (str,):
        kind = DataKind.STRING
    elif base in (bytes, bytearray, memoryview):
        kind = DataKind.BYTES
    elif base in (bool,):
        kind = DataKind.BOOL
    elif base in (int,):
        kind = DataKind.INT
    elif base in (float,):
        kind = DataKind.FLOAT
    elif base in (_dc.Decimal,):
        kind = DataKind.DECIMAL
    elif base in (_dt.datetime,):
        kind = DataKind.DATETIME
    elif base in (_dt.date,):
        kind = DataKind.DATE
    elif base in (_dt.time,):
        kind = DataKind.TIME
    elif base in (_uuid.UUID,):
        kind = DataKind.UUID
    else:
        # mappings / unknowns -> JSON (wire schema handles details)
        if origin in (dict, Dict):
            kind = DataKind.JSON
        else:
            # If it's an Annotated[str, ...] it already fell into STRING; other unknowns -> JSON
            kind = DataKind.JSON

    # 6) SA type plan (declarative)
    sa = _plan_sa_type(
        kind,
        py_info,
        prefer_dialect=prefer_dialect,
        max_length=max_length,
        decimal_precision=decimal_precision,
        decimal_scale=decimal_scale,
    )

    # 7) JSON docs hint
    jh = _json_hint(kind, py_info, max_length=max_length)

    return Inferred(
        kind=kind,
        py=py_info,
        sa=sa,
        json=jh,
        nullable=is_opt,
    )


# ──────────────────────────────────────────────────────────────────────────────
# SA type planning (strings, numerics, UUID/JSON/ARRAY/Enum)
# ──────────────────────────────────────────────────────────────────────────────


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
        # Prefer native PG UUID if available; otherwise fall back to CHAR(32)/String in adapters
        if d == "postgresql":
            return SATypePlan(
                name="UUID", args=(), kwargs={"as_uuid": True}, dialect="postgresql"
            )
        return SATypePlan(name="String", args=(36,), kwargs={}, dialect=None)

    if kind is DataKind.JSON:
        # Prefer JSONB on PG; adapters can map to JSON elsewhere
        if d == "postgresql":
            return SATypePlan(name="JSONB", args=(), kwargs={}, dialect="postgresql")
        return SATypePlan(name="JSON", args=(), kwargs={}, dialect=None)

    if kind is DataKind.ENUM:
        if not py.enum_cls:
            raise InferenceError("ENUM kind requires enum_cls in PyTypeInfo")
        # Native DB enum; adapters can choose name/schema etc.
        return SATypePlan(
            name="Enum", args=(py.enum_cls,), kwargs={"native_enum": True}, dialect=None
        )

    if kind is DataKind.ARRAY:
        if not py.array_item:
            raise InferenceError("ARRAY kind requires array_item in PyTypeInfo")
        # The element type name is derived from the nested SATypePlan.
        elem_plan = _plan_sa_type(
            # Use nested kind based on base guess; we only need name here
            _nested_kind_from_py(py.array_item),
            py.array_item,
            prefer_dialect=prefer_dialect,
            max_length=None,
            decimal_precision=None,
            decimal_scale=None,
        )
        # ARRAY is dialect-specific in SA; prefer postgresql.ARRAY
        if prefer_dialect == "postgresql":
            return SATypePlan(
                name="ARRAY",
                args=(
                    elem_plan.name,
                ),  # downstream adapter replaces with actual SA type object
                kwargs={},
                dialect="postgresql",
            )
        # Non-PG adapters: map ARRAY to JSON as a fallback
        return SATypePlan(name="JSON", args=(), kwargs={}, dialect=None)

    raise UnsupportedType(f"Cannot plan SA type for kind={kind!r}")


def _nested_kind_from_py(nested_py: PyTypeInfo) -> DataKind:
    # Reasonable default mapping for element-kind re-planning
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


# ──────────────────────────────────────────────────────────────────────────────
# JSON-hint planning (for OpenAPI/docs shaping only)
# ──────────────────────────────────────────────────────────────────────────────


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
        return JsonHint(
            type="string", enum=[e.name for e in py.enum_cls]
        )  # names for docs
    if kind is DataKind.ARRAY and py.array_item:
        # Nest using best-effort element hint (default STRING for unknowns)
        elem_kind = _nested_kind_from_py(py.array_item)
        return JsonHint(
            type="array", items=_json_hint(elem_kind, py.array_item, max_length=None)
        )
    # Fallback
    return JsonHint(type="string")
