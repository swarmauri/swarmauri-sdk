from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Type


# ---------------------------------------------------------------------------
# Public markers (wire/adapters provide validation/normalization at runtime)
# ---------------------------------------------------------------------------


class Email:
    """Marker indicating email string semantics."""


class Phone:
    """Marker indicating E.164 phone string semantics."""


# ---------------------------------------------------------------------------
# Portable data-kind (DB- and adapter-agnostic)
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Structured outputs
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PyTypeInfo:
    """Normalized info about the Python-side type annotation."""

    base: Any
    is_optional: bool = False
    enum_cls: Optional[Type[Enum]] = None
    array_item: Optional["PyTypeInfo"] = None
    annotated: Tuple[Any, ...] = ()


@dataclass(frozen=True)
class SATypePlan:
    """Declarative plan for constructing an SA column type downstream."""

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


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class InferenceError(ValueError):
    """Base class for inference-related errors."""


class UnsupportedType(InferenceError):
    """Raised when a type cannot be inferred."""
