"""Example ORM tables used for demos and tests."""

import datetime as dt
from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

from .mixins import (
    GUIDPk,
    MaskableEdge,
    RelationEdge,
    Slugged,
    TenantBound,
    Timestamped,
    Audited,
)
from .v2.tables._base import Base


class Change(Base):
    __tablename__ = "changes"
    seq = Column(BigInteger, primary_key=True, autoincrement=True)
    at = Column(DateTime, default=dt.datetime.utcnow)
    actor_id = Column(UUID, ForeignKey("users.id"))
    table_name = Column(String)
    row_id = Column(UUID)
    action = Column(String)  # insert | update | delete
    diff = Column(JSONB)


# ────────── RBAC ------------------------------------------------------
class Role(Base, GUIDPk, TenantBound, Slugged, Timestamped, Audited):
    __tablename__ = "roles"
    global_mask = Column(Integer, default=0)  # platform / tenant admin bits


class RolePerm(
    Base, GUIDPk, TenantBound, RelationEdge, MaskableEdge, Timestamped, Audited
):
    __tablename__ = "role_perms"  # role ↔ resource
    role_id = Column(UUID, ForeignKey("roles.id"), nullable=False)
    target_table = Column(String, nullable=False)  # generic
    target_id = Column(UUID, nullable=False)  # row / sentinel


class RoleGrant(Base, GUIDPk, TenantBound, RelationEdge, Timestamped, Audited):
    __tablename__ = "role_grants"  # principal ↔ role
    principal_id = Column(UUID, nullable=False)  # user / group
    role_id = Column(UUID, ForeignKey("roles.id"), nullable=False)
