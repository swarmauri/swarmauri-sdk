import datetime as dt
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, String, Integer, JSON, DateTime, ForeignKey, BigInteger, MetaData

from . import Base
from ..mixins import (
    GUIDPk, 
    Timestamped, 
    TenantBound, 
    Principal, 
    RelationEdge,
    Timestamped, 
    MaskableEdge,
    AsyncCapable
)


# ───────── tenancy core ──────────────────────────────────────────────────
class Tenant(Base, GUIDPk, Timestamped):
    __tablename__ = "tenants"
    email        = Column(String, unique=True)

class User(Base, GUIDPk, Timestamped, TenantBound, Principal, AsyncCapable):
    __tablename__ = "users"
    email        = Column(String, unique=True)

class Group(Base, GUIDPk, Timestamped, TenantBound, Principal):
    __tablename__ = "groups"
    name         = Column(String)


__all__ = ["Tenant", "User", "Group"]


for _name in list(globals()):
    if _name not in __all__ and not _name.startswith("__"):
        del globals()[_name]

def __dir__():
    # optional, keeps IPython completion tight
    return sorted(__all__)