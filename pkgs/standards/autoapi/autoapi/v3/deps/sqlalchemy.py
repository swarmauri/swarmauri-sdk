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


# ── Custom Extensions / Generics ─────────────────────────────────────────
DateTime = _DateTime(timezone=False)
TZDateTime = _DateTime(timezone=True)


class PgUUID(_PgUUID):
    @property
    def hex(self):
        return self.as_uuid.hex


# ── Public Exports ───────────────────────────────────────────────────────
__all__ = [
    # Core types
    "Boolean",
    "Column",
    "DateTime",
    "TZDateTime",
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
    "PgUUID",
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
