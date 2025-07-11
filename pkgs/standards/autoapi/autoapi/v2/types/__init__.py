# ── third-party ───────────────────────────────────────────────────────────
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SAEnum,
    Text,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    String,
    UniqueConstraint,
    event,
)
from sqlalchemy.dialects.postgresql import (
    ARRAY,
    ENUM as PgEnum,
    JSONB,
    UUID,
    TSVECTOR
)
from sqlalchemy.orm import (
    Mapped,
    declarative_mixin,
    declared_attr,
    foreign,
    mapped_column,
    relationship,
    remote,
)
from sqlalchemy.ext.mutable import MutableDict, MutableList

# ── local package ─────────────────────────────────────────────────────────
from .op import _Op, _SchemaVerb

# ── monkey-patch JSON types so AutoAPI schema reflection works ────────────
JSON.python_type = dict   # type: ignore[attr-defined]
JSONB.python_type = dict  # type: ignore[attr-defined]

# ── public re-exports ─────────────────────────────────────────────────────
__all__: list[str] = [
    # local
    "_Op",
    "_SchemaVerb",
    # sqlalchemy core
    "Boolean",
    "Column",
    "DateTime",
    "SAEnum",
    "ForeignKey",
    "Index",
    "Integer",
    "JSON",
    "Numeric",
    "String",
    "UniqueConstraint",
    "event",
    # sqlalchemy.dialects.postgresql
    "ARRAY",
    "PgEnum",
    "JSONB",
    "UUID",
    "TSVECTOR",
    # sqlalchemy.orm
    "Mapped",
    "declarative_mixin",
    "declared_attr",
    "foreign",
    "mapped_column",
    "relationship",
    "remote",
    # sqlalchemy.ext.mutable
    "MutableDict",
    "MutableList",
]
