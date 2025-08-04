# ── third-party ───────────────────────────────────────────────────────────
from types import MethodType, SimpleNamespace
from uuid import uuid4, UUID
from sqlalchemy import (
    Boolean,
    Column,
    DateTime as _DateTime,
    Enum as SAEnum,
    Text,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    String,
    LargeBinary,
    UniqueConstraint,
    CheckConstraint,
    event,
)
from sqlalchemy.dialects.postgresql import (
    ARRAY,
    ENUM as PgEnum,
    JSONB,
    UUID as PgUUID,
    TSVECTOR,
)
from sqlalchemy.orm import (
    Mapped,
    declarative_mixin,
    declared_attr,
    foreign,
    mapped_column,
    relationship,
    remote,
    column_property,
    Session,
)

from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.ext.hybrid import hybrid_property

# ── local package ─────────────────────────────────────────────────────────
from .op import _Op, _SchemaVerb
from .authn_abc import AuthNProvider
from .table_config_provider import TableConfigProvider
from .hook_provider import HookProvider
from .nested_path_provider import NestedPathProvider
from .allow_anon_provider import AllowAnonProvider

DateTime = _DateTime(timezone=False)
TZDateTime = _DateTime(timezone=True)

# ── public re-exports ─────────────────────────────────────────────────────
__all__: list[str] = [
    # local
    "_Op",
    "_SchemaVerb",
    "AuthNProvider",
    "TableConfigProvider",
    "HookProvider",
    "NestedPathProvider",
    "AllowAnonProvider",
    # builtin types
    "MethodType",
    "SimpleNamespace",
    # sqlalchemy core
    "Boolean",
    "Column",
    "DateTime",
    "TZDateTime",
    "Text",
    "SAEnum",
    "ForeignKey",
    "Index",
    "Integer",
    "JSON",
    "Numeric",
    "String",
    "LargeBinary",
    "UniqueConstraint",
    "CheckConstraint",
    "event",
    # sqlalchemy.dialects.postgresql
    "ARRAY",
    "PgEnum",
    "JSONB",
    "PgUUID",
    "TSVECTOR",
    # sqlalchemy.orm
    "Mapped",
    "declarative_mixin",
    "declared_attr",
    "foreign",
    "mapped_column",
    "column_property",
    "hybrid_property",
    "relationship",
    "remote",
    "Session",
    # sqlalchemy.ext.mutable
    "MutableDict",
    "MutableList",
    # uuid convenience
    "uuid4",
    "UUID",
]
