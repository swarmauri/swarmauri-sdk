# ── Standard Library ─────────────────────────────────────────────────────
from types import MethodType, SimpleNamespace
from uuid import uuid4, UUID

# ── Third-party Dependencies (via deps module) ───────────────────────────
from ..deps.sqlalchemy import (
    # Core SQLAlchemy
    Boolean,
    Column,
    DateTime,
    TZDateTime,
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
    event,
    # PostgreSQL dialect
    ARRAY,
    PgEnum,
    JSONB,
    PgUUID,
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
    InstrumentedAttribute,
    # Extensions
    MutableDict,
    MutableList,
    hybrid_property,
)

from ..deps.pydantic import (
    BaseModel,
    Field,
    ValidationError,
)

from ..deps.fastapi import (
    APIRouter,
    Router,
    Security,
    Depends,
    Request,
    Response,
    Path,
    Body,
    HTTPException,
    App,
)

# ── Local Package ─────────────────────────────────────────────────────────
from .op import _Op, _SchemaVerb
from .authn_abc import AuthNProvider
from .table_config_provider import TableConfigProvider
from .hook_provider import HookProvider
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


# ── Public Re-exports (Backwards Compatibility) ──────────────────────────
__all__: list[str] = [
    # local
    "_Op",
    "_SchemaVerb",
    "AuthNProvider",
    "TableConfigProvider",
    "HookProvider",
    "NestedPathProvider",
    "AllowAnonProvider",
    "RequestExtrasProvider",
    "ResponseExtrasProvider",
    "OpVerbAliasProvider",
    "list_verb_alias_providers",
    "list_request_extras_providers",
    "list_response_extras_providers",
    "OpConfigProvider",
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
    "InstrumentedAttribute",
    # sqlalchemy.ext.mutable (from deps.sqlalchemy)
    "MutableDict",
    "MutableList",
    # pydantic schema support (from deps.pydantic)
    "BaseModel",
    "Field",
    "ValidationError",
    # fastapi support (from deps.fastapi)
    "Request",
    "Response",
    "APIRouter",
    "Router",
    "App",
    "Security",
    "Depends",
    "Path",
    "Body",
    "HTTPException",
]
