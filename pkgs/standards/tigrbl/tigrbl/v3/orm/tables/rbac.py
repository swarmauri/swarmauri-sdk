from uuid import UUID


from ...specs import IO, F, acol, S
from ...specs.storage_spec import ForeignKeySpec
from ...types import Integer, String, PgUUID, Mapped

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
    slug: Mapped[str] = acol(
        storage=S(String, unique=True),
        field=F(),
        io=IO(),
    )
    global_mask: Mapped[int] = acol(
        storage=S(Integer, default=0),
        field=F(),
        io=IO(),
    )


class RolePerm(Base, GUIDPk, Timestamped, TenantBound, RelationEdge, MaskableEdge):
    __tablename__ = "role_perms"
    role_id: Mapped[UUID] = acol(
        storage=S(PgUUID, fk=ForeignKeySpec("roles.id")),
        field=F(),
        io=IO(),
    )
    target_table: Mapped[str] = acol(
        storage=S(String),
        field=F(),
        io=IO(),
    )
    target_id: Mapped[str] = acol(
        storage=S(String),
        field=F(),
        io=IO(),
    )  # row or sentinel


class RoleGrant(Base, GUIDPk, Timestamped, TenantBound, RelationEdge):
    __tablename__ = "role_grants"
    principal_id: Mapped[UUID] = acol(
        storage=S(PgUUID),
        field=F(),
        io=IO(),
    )  # FK to principal row
    role_id: Mapped[UUID] = acol(
        storage=S(PgUUID, fk=ForeignKeySpec("roles.id")),
        field=F(),
        io=IO(),
    )


__all__ = ["Role", "RolePerm", "RoleGrant"]

for _name in list(globals()):
    if _name not in __all__ and not _name.startswith("__"):
        del globals()[_name]


def __dir__():
    """Tighten ``dir()`` output for interactive sessions."""

    return sorted(__all__)
