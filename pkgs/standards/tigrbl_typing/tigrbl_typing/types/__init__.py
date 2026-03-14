# ── Standard Library ─────────────────────────────────────────────────────
from types import MethodType, SimpleNamespace
from uuid import uuid4, UUID

# ── Third-party Dependencies (via deps module) ───────────────────────────
from ..vendor.sqlalchemy import (
    # Core SQLAlchemy
    Boolean,
    Column,
    _DateTime,
    SAEnum,
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
    create_engine,
    event,
    # PostgreSQL dialect
    ARRAY,
    PgEnum,
    JSONB,
    TSVECTOR,
    # ORM
    Mapped,
    declarative_mixin,
    declared_attr,
    foreign,
    mapped_column,
    relationship,
    remote,
    column_property,
    Session,
    sessionmaker,
    InstrumentedAttribute,
    # Extensions
    MutableDict,
    MutableList,
    hybrid_property,
    StaticPool,
    TypeDecorator,
)


from ..vendor.pydantic import (
    BaseModel,
    Field,
    ValidationError,
)

from ..status.exceptions import StatusDetailError

# ── Local Package ─────────────────────────────────────────────────────────
from .op import _Op, _SchemaVerb
from .uuid import PgUUID, SqliteUUID


# ── Generics / Extensions ─────────────────────────────────────────────────
DateTime = _DateTime(timezone=False)
TZDateTime = _DateTime(timezone=True)


# ── Public Re-exports (Backwards Compatibility) ──────────────────────────
__all__: list[str] = [
    # local
    "_Op",
    "_SchemaVerb",
    # add ons
    "SqliteUUID",
    # builtin types
    "MethodType",
    "SimpleNamespace",
    "uuid4",
    "UUID",
    # sqlalchemy core (from deps.sqlalchemy)
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
    "create_engine",
    "event",
    # sqlalchemy.dialects.postgresql (from deps.sqlalchemy)
    "ARRAY",
    "PgEnum",
    "JSONB",
    "PgUUID",
    "TSVECTOR",
    # sqlalchemy.orm (from deps.sqlalchemy)
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
    "sessionmaker",
    "InstrumentedAttribute",
    # sqlalchemy.ext.mutable (from deps.sqlalchemy)
    "MutableDict",
    "MutableList",
    "StaticPool",
    "TypeDecorator",
    # pydantic schema support (from deps.pydantic)
    "BaseModel",
    "Field",
    "ValidationError",
    # status
    "StatusDetailError",
]
