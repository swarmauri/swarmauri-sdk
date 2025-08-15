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
    UUID as _PgUUID,
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


from pydantic import Field, ValidationError

from fastapi import (
    APIRouter,
    Security,
    Depends,
    Request,
    Response,
    Path,
    Body,
    HTTPException,
)

# ── local package ─────────────────────────────────────────────────────────
from .op import _Op, _SchemaVerb
from .authn_abc import AuthNProvider
from .table_config_provider import TableConfigProvider
from .nested_path_provider import NestedPathProvider
from .allow_anon_provider import AllowAnonProvider
from .request_extras_provider import (
    RequestExtrasProvider,
    list_request_extras_providers,
)
from .response_extras_provider import (
    ResponseExtrasProvider,
    list_response_extras_providers,
)

from .op_verb_alias_provider import OpVerbAliasProvider, list_verb_alias_providers
from .op_config_provider import OpConfigProvider


# ── Generics / Extensions ─────────────────────────────────────────────────
DateTime = _DateTime(timezone=False)
TZDateTime = _DateTime(timezone=True)


class PgUUID(_PgUUID):
    @property
    def hex(self):
        return self.as_uuid.hex


# ── public re-exports ─────────────────────────────────────────────────────
__all__: list[str] = [
    # local
    "_Op",
    "_SchemaVerb",
    "AuthNProvider",
    "TableConfigProvider",
    "NestedPathProvider",
    "AllowAnonProvider",
    "RequestExtrasProvider",
    "ResponseExtrasProvider",
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
    # pydantic schema support
    "Field",
    "ValidationError",
    # fastapi support
    "Request",
    "Response",
    "APIRouter",
    "Security",
    "Depends",
    "Path",
    "Body",
    "HTTPException",
]

__all__ += [
    "OpVerbAliasProvider",
    "list_verb_alias_providers",
    "list_request_extras_providers",
    "list_response_extras_providers",
]


__all__ += ["OpConfigProvider"]
