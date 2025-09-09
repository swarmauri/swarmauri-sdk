# ── SQLAlchemy Core ──────────────────────────────────────────────────────
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
    create_engine,
    event,
)

# ── SQLAlchemy PostgreSQL Dialect ────────────────────────────────────────
from sqlalchemy.dialects.postgresql import (
    ARRAY,
    ENUM as PgEnum,
    JSONB,
    UUID as _PgUUID,
    TSVECTOR,
)

# ── SQLAlchemy ORM ───────────────────────────────────────────────────────
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
    sessionmaker,
    InstrumentedAttribute,
)

from sqlalchemy.pool import StaticPool

# ── SQLAlchemy Extensions ────────────────────────────────────────────────
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.ext.hybrid import hybrid_property


# ── Public Exports ───────────────────────────────────────────────────────
__all__ = [
    # Core types
    "Boolean",
    "Column",
    "_DateTime",
    "SAEnum",
    "Text",
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
    "StaticPool",
    "event",
    # PostgreSQL dialect
    "ARRAY",
    "PgEnum",
    "JSONB",
    "_PgUUID",
    "TSVECTOR",
    # ORM
    "Mapped",
    "declarative_mixin",
    "declared_attr",
    "foreign",
    "mapped_column",
    "relationship",
    "remote",
    "column_property",
    "Session",
    "sessionmaker",
    "InstrumentedAttribute",
    # Extensions
    "MutableDict",
    "MutableList",
    "hybrid_property",
]
