from uuid import UUID

from ..specs import acol, S
from ..specs.storage_spec import ForeignKeySpec
from ..types import Integer, String, PgUUID

from . import Base
from ..mixins import (
    GUIDPk,
    TenantBound,
    RelationEdge,
    Timestamped,
    MaskableEdge,
)


# ───────── RBAC core ──────────────────────────────────────────────────
class Role(Base, GUIDPk, Timestamped, TenantBound):
    __tablename__ = "roles"
    slug: str = acol(storage=S(String, unique=True))
    global_mask: int = acol(
        storage=S(Integer, default=0),
    )


class RolePerm(Base, GUIDPk, Timestamped, TenantBound, RelationEdge, MaskableEdge):
    __tablename__ = "role_perms"
    role_id: UUID = acol(
        storage=S(PgUUID, fk=ForeignKeySpec("roles.id")),
    )
    target_table: str = acol(storage=S(String))
    target_id: str = acol(storage=S(String))  # row or sentinel


class RoleGrant(Base, GUIDPk, Timestamped, TenantBound, RelationEdge):
    __tablename__ = "role_grants"
    principal_id: UUID = acol(storage=S(PgUUID))  # FK to principal row
    role_id: UUID = acol(
        storage=S(PgUUID, fk=ForeignKeySpec("roles.id")),
    )


__all__ = ["Role", "RolePerm", "RoleGrant"]

for _name in list(globals()):
    if _name not in __all__ and not _name.startswith("__"):
        del globals()[_name]


def __dir__():
    """Tighten ``dir()`` output for interactive sessions."""

    return sorted(__all__)
