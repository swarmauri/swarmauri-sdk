from ..types import Column, Integer, String, ForeignKey, PgUUID

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
    slug = Column(String, unique=True)
    global_mask = Column(Integer, default=0)


class RolePerm(Base, GUIDPk, Timestamped, TenantBound, RelationEdge, MaskableEdge):
    __tablename__ = "role_perms"
    role_id = Column(PgUUID(as_uuid=True), ForeignKey("roles.id"))
    target_table = Column(String)
    target_id = Column(String)  # row or sentinel


class RoleGrant(Base, GUIDPk, Timestamped, TenantBound, RelationEdge):
    __tablename__ = "role_grants"
    principal_id = Column(PgUUID(as_uuid=True))  # FK to principal row
    role_id = Column(PgUUID(as_uuid=True), ForeignKey("roles.id"))


__all__ = ["Role", "RolePerm", "RoleGrant"]

for _name in list(globals()):
    if _name not in __all__ and not _name.startswith("__"):
        del globals()[_name]


def __dir__():
    """Tighten ``dir()`` output for interactive sessions."""

    return sorted(__all__)
