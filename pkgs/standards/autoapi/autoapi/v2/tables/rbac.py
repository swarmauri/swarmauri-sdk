import datetime as dt
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, Integer, JSON, DateTime, ForeignKey, BigInteger, MetaData
from sqlalchemy.orm import DeclarativeBase

from . import Base
from ..mixins import GUIDPk, Timestamped, TenantBound, Principal, RelationEdge, Timestamped, MaskableEdge

# ───────── RBAC core ──────────────────────────────────────────────────
class Role(Base, GUIDPk, Timestamped, TenantBound):
    __tablename__ = "roles"
    slug         = Column(String, unique=True)
    global_mask  = Column(Integer, default=0)

class RolePerm(Base, GUIDPk, Timestamped, TenantBound,
               RelationEdge, MaskableEdge):
    __tablename__ = "role_perms"
    role_id       = Column(String, ForeignKey("roles.id"))
    target_table  = Column(String)
    target_id     = Column(String)                # row or sentinel

class RoleGrant(Base, GUIDPk, Timestamped, TenantBound,
                RelationEdge):
    __tablename__ = "role_grants"
    principal_id  = Column(String)                # FK to principal row
    role_id       = Column(String, ForeignKey("roles.id"))
