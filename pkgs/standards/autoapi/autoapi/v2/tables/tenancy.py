import datetime as dt
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, String, Integer, JSON, DateTime, ForeignKey, BigInteger, MetaData

from . import Base
from ..mixins import GUIDPk, Timestamped, TenantBound, Principal, RelationEdge, Timestamped, MaskableEdge


# ───────── tenancy core ──────────────────────────────────────────────────
class Tenant(Base, GUIDPk, Timestamped):
    __tablename__ = "tenants"
    email        = Column(String, unique=True)

class User(Base, GUIDPk, Timestamped, TenantBound, Principal):
    __tablename__ = "users"
    email        = Column(String, unique=True)

class Group(Base, GUIDPk, Timestamped, TenantBound, Principal):
    __tablename__ = "groups"
    name         = Column(String)
