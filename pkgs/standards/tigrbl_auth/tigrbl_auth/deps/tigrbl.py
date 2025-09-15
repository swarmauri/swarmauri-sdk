"""tigrbl framework dependencies re-exported for tigrbl_auth."""

from tigrbl import TigrblApi, TigrblApp, hook_ctx, op_ctx
from tigrbl.engine import HybridSession as AsyncSession, engine as build_engine
from tigrbl.config.constants import TIGRBL_AUTH_CONTEXT_ATTR
from tigrbl.types.authn_abc import AuthNProvider
from tigrbl.types import (
    Mapped,
    String,
    JSON,
    PgUUID,
    TZDateTime,
    Boolean,
    Integer,
    LargeBinary,
    UUID,
    relationship,
)
from tigrbl.orm.tables import (
    Base,
    Client as ClientBase,
    Tenant as TenantBase,
    User as UserBase,
)
from tigrbl.orm.mixins import (
    Bootstrappable,
    Timestamped,
    TenantColumn,
    UserColumn,
)
from tigrbl.specs import F, S, IO, acol, ColumnSpec
from tigrbl.column.storage_spec import ForeignKeySpec
from tigrbl.error import IntegrityError

__all__ = [
    "TigrblApi",
    "TigrblApp",
    "hook_ctx",
    "op_ctx",
    "AsyncSession",
    "build_engine",
    "TIGRBL_AUTH_CONTEXT_ATTR",
    "AuthNProvider",
    "Mapped",
    "String",
    "JSON",
    "PgUUID",
    "TZDateTime",
    "Boolean",
    "Integer",
    "LargeBinary",
    "UUID",
    "relationship",
    "Base",
    "ClientBase",
    "TenantBase",
    "UserBase",
    "Bootstrappable",
    "Timestamped",
    "TenantColumn",
    "UserColumn",
    "F",
    "S",
    "IO",
    "acol",
    "ColumnSpec",
    "ForeignKeySpec",
    "IntegrityError",
]
