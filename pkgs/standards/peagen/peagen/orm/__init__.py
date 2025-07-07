"""
condensed_orm.py  –  all Peagen domain tables in one place
(uses only sqlalchemy.Column – no mapped_column / JSONB).
"""

from __future__ import annotations
import uuid, datetime as dt
from typing import Any, Dict

from sqlalchemy import (
    Column, String, DateTime, Boolean, Integer, ForeignKey, Enum as SAEnum,
    JSON, Numeric, Table
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

# ---------------------------------------------------------------------
# bring in the baseline tables that AutoAPI already owns
# ---------------------------------------------------------------------
from autoapi.v2.tables     import Tenant, User
from autoapi.v2.tables     import Role, RoleGrant, RolePerm
from autoapi.v2.tables     import StatusEnum

from autoapi.v2.tables     import Base
from autoapi.v2.mixins      import (
    GUIDPk, Timestamped, TenantBound, OwnerBound, AsyncCapable,
    Replaceable, BulkCapable, StatusEnum as StatusMixin, BlobRef
)

# ---------------------------------------------------------------------
# 1) association edges
# ---------------------------------------------------------------------

class UserTenant(Base):
    """
    Many-to-many edge between users and tenants.
    A user may be invited to / removed from any number of tenants.
    """
    __tablename__  = "user_tenants"
    tenant_id      = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), primary_key=True)
    user_id        = Column(UUID(as_uuid=True), ForeignKey("users.id"),  primary_key=True)
    joined_at      = Column(DateTime, default=dt.datetime.utcnow, nullable=False)

    # bidirectional convenience
    tenant = relationship(Tenant, backref="memberships")
    user   = relationship(User,   backref="tenancies")


class UserRepository(Base):
    """
    Edge capturing *any* per-repository permission or ownership
    the user may have.  `perm` can be "owner", "push", "pull", etc.
    """
    __tablename__  = "user_repositories"
    repository_id  = Column(UUID(as_uuid=True), ForeignKey("repositories.id"), primary_key=True)
    user_id        = Column(UUID(as_uuid=True), ForeignKey("users.id"),        primary_key=True)

# ---------------------------------------------------------------------
# 2) Repository hierarchy
# ---------------------------------------------------------------------

class Repository(Base, GUIDPk, Timestamped, TenantBound, StatusMixin):
    """
    A code or data repository that lives under a tenant.
    – parent of Secrets & DeployKeys
    """
    __tablename__ = "repositories"
    __table_args__ = (
        UniqueConstraint("url", name="uq_repositories_url"),
        UniqueConstraint("tenant_id", "name", name="uq_repositories_tenant_name"),
    )
    name       = Column(String, nullable=False)
    url        = Column(String, unique=True, nullable=False)
    default_branch = Column(String, default="main")
    commit_sha: = Column(String(length=40), nullable=True)
    remote_name: Column(String, nullable=False, default="origin")

    # relationships
    secrets     = relationship("Secret",     back_populates="repository", cascade="all, delete-orphan")
    deploy_keys = relationship("DeployKey",  back_populates="repository", cascade="all, delete-orphan")
    users       = relationship(User, secondary="user_repositories", backref="repositories")

# ---------------------------------------------------------------------
# 3) Secret & DeployKey now point to Repository, not Tenant
# ---------------------------------------------------------------------

class Secret(Base, GUIDPk, Timestamped):
    __tablename__ = "secrets"
    __table_args__ = (
        UniqueConstraint("repository_id", "name", "version",
                         name="uq_secret_repo_name_ver"),
    )
    repository_id = Column(UUID(as_uuid=True), ForeignKey("repositories.id"), nullable=False)
    name          = Column(String, nullable=False)
    cipher        = Column(String, nullable=False)
    version       = Column(Integer, default=0, nullable=False)

    repository = relationship(Repository, back_populates="secrets")


class DeployKey(Base, GUIDPk, Timestamped):
    __tablename__ = "deploy_keys"
    __table_args__ = (
        UniqueConstraint("repository_id", "public_key", name="uq_deploykey_repo_key"),
    )
    repository_id = Column(UUID(as_uuid=True), ForeignKey("repositories.id"), nullable=False)
    user_id        = Column(UUID(as_uuid=True), ForeignKey("users.id"),  primary_key=True)
    public_key    = Column(String, nullable=False)
    read_only     = Column(Boolean, default=True)

    repository = relationship(Repository, back_populates="deploy_keys")


# ---------------------------------------------------------------------
# 4) Execution / queue objects (unchanged parents but FK tweaks)
# ---------------------------------------------------------------------

class Pool(Base, GUIDPk, Timestamped, TenantBound):
    __tablename__ = "pools"
    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_pools_tenant_name"),
    )
    name          = Column(String, nullable=False, unique=True)


class Worker(Base, GUIDPk, Timestamped):
    __tablename__ = "workers"
    pool_id       = Column(UUID(as_uuid=True), ForeignKey("pools.id"), nullable=False)
    url           = Column(String, nullable=False)
    advertises    = Column(JSON, nullable=True)

    pool = relationship(Pool, backref="workers")


class Task(Base, GUIDPk, Timestamped, TenantBound):
    """
    *Definition* of a task (immutable intent + metadata).
    """
    __tablename__ = "tasks"
    pool_id       = Column(UUID(as_uuid=True), ForeignKey("pools.id"), nullable=False)
    payload       = Column(JSON, nullable=True)
    labels        = Column(JSON, nullable=True)
    note          = Column(String, nullable=True)
    status        = Column(SAEnum(*StatusMixin.__annotations__['status'].type.enums,
                                  name="status_enum"), default="waiting")

    pool  = relationship(Pool, backref="tasks")
    works = relationship("Work", back_populates="task", cascade="all, delete-orphan")


class Work(Base, GUIDPk, Timestamped):
    """
    One execution attempt of a Task (retries generate multiple Work rows).
    """
    __tablename__ = "works"
    task_id       = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    status        = Column(SAEnum(*StatusMixin.__annotations__['status'].type.enums,
                                  name="status_enum"), default="queued")
    result        = Column(JSON, nullable=True)
    duration_s    = Column(Integer)

    task = relationship(Task, back_populates="works")


# ---------------------------------------------------------------------
# 5) Raw blobs (stand-alone)
# ---------------------------------------------------------------------

class RawBlob(Base, GUIDPk, Timestamped, BlobRef):
    __tablename__ = "raw_blobs"
    mime_type = Column(String, nullable=False)
    size      = Column(Integer, nullable=False)
