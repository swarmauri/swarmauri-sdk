"""
peagen/orm/__init__.py  –  all Peagen domain tables in one place
(uses only sqlalchemy.Column – no mapped_column / JSONB).
"""

from __future__ import annotations

from typing import FrozenSet
from enum import Enum, auto

from autoapi.v2.types import (
    JSON,
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    CheckConstraint,
    PgEnum,
    PgUUID,
    MutableDict,
    relationship,
    foreign,
    remote,
    declarative_mixin,
    declared_attr,
)

# ---------------------------------------------------------------------
# bring in the baseline tables that AutoAPI already owns
# ---------------------------------------------------------------------
from autoapi.v2.tables import Tenant as TenantBase, User as UserBase, Org
from autoapi.v2.tables import Role, RoleGrant, RolePerm
from autoapi.v2.tables import Status
from autoapi.v2.tables import Base
from autoapi.v2.mixins import (
    GUIDPk,
    # TenantMixin,
    UserMixin,
    OrgMixin,
    Ownable,
    Bootstrappable,
    Timestamped,
    TenantBound,
    StatusMixin,
    BlobRef,
)
from peagen.defaults import (
    DEFAULT_POOL_NAME,
    DEFAULT_POOL_ID,
    DEFAULT_TENANT_ID,
    # DEFAULT_TENANT_EMAIL,
    # DEFAULT_TENANT_NAME,
    # DEFAULT_TENANT_SLUG,
    # DEFAULT_SUPER_USER_ID,
    # DEFAULT_SUPER_USER_EMAIL,
    # DEFAULT_SUPER_USER_ID_2,
    # DEFAULT_SUPER_USER_EMAIL_2
)


# ---------------------------------------------------------------------


def _is_terminal(cls, state: str | Status) -> bool:
    """Return True if *state* represents completion."""
    terminal: FrozenSet[str] = frozenset({"success", "failed", "cancelled", "rejected"})
    value = state.value if isinstance(state, Status) else state
    return value in terminal


Status.is_terminal = classmethod(_is_terminal)


# ---------------------------------------------------------------------
# Repository hierarchy
# ---------------------------------------------------------------------
class Tenant(TenantBase, Bootstrappable):
    pass
    # DEFAULT_ROWS = [
    #     {
    #         "id": DEFAULT_TENANT_ID,
    #         "email": DEFAULT_TENANT_EMAIL,
    #         "name": DEFAULT_TENANT_NAME,
    #         "slug": DEFAULT_TENANT_SLUG,
    #     }
    # ]


class User(UserBase, Bootstrappable):
    pass
    # DEFAULT_ROWS = [
    #     {
    #         "id": DEFAULT_SUPER_USER_ID,
    #         "email": DEFAULT_SUPER_USER_EMAIL,
    #         "tenant_id": DEFAULT_TENANT_ID,
    #     },
    #     {
    #         "id": DEFAULT_SUPER_USER_ID_2,
    #         "email": DEFAULT_SUPER_USER_EMAIL_2,
    #         "tenant_id": DEFAULT_TENANT_ID,
    #     }
    # ]


class Repository(Base, GUIDPk, Timestamped, TenantBound, Ownable, StatusMixin):
    """
    A code or data repository that lives under a tenant.
    – parent of Secrets & DeployKeys
    """

    __tablename__ = "repositories"
    __table_args__ = (
        UniqueConstraint("url"),
        UniqueConstraint("tenant_id", "name"),
    )
    name = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    default_branch = Column(String, default="main")
    commit_sha = Column(String(length=40), nullable=True)
    remote_name = Column(String, nullable=False, default="origin")

    secrets = relationship(
        "RepoSecret", back_populates="repository", cascade="all, delete-orphan"
    )
    deploy_keys = relationship(
        "DeployKey", back_populates="repository", cascade="all, delete-orphan"
    )
    tasks = relationship(
        "Task",
        back_populates="repository",
        cascade="all, delete-orphan",
    )


@declarative_mixin
class RepositoryMixin:
    repository_id = Column(
        PgUUID(as_uuid=True), ForeignKey("repositories.id"), nullable=False
    )


class RepositoryRefMixin:
    repository_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=True,  # ← changed
    )
    repo = Column(String, nullable=False)  # e.g. "github.com/acme/app"
    ref = Column(String, nullable=False)  # e.g. "main" / SHA / tag

    @declared_attr
    def repository(cls):
        from peagen.orm import Repository  # late import

        return relationship(
            "Repository",
            back_populates="tasks",
            primaryjoin=foreign(cls.repository_id) == remote(Repository.id),
        )


# ---------------------------------------------------------------------
# association edges
# ---------------------------------------------------------------------


# class UserTenant(Base, GUIDPk, TenantMixin, UserMixin):
#     """
#     Many-to-many edge between users and tenants.
#     A user may be invited to / removed from any number of tenants.
#     """

#     __tablename__ = "user_tenants"
#     joined_at = Column(tzutcnow, default=dt.timezone.utcnow, nullable=False)


class UserRepository(Base, GUIDPk, RepositoryMixin, UserMixin):
    """
    Edge capturing *any* per-repository permission or ownership
    the user may have.  `perm` can be "owner", "push", "pull", etc.
    """

    __tablename__ = "user_repositories"


# ---------------------------------------------------------------------
# 3) Keys
# ---------------------------------------------------------------------


class PublicKey(Base, GUIDPk, UserMixin, Timestamped):
    __tablename__ = "public_keys"
    __table_args__ = (UniqueConstraint("user_id", "public_key"),)
    title = Column(String, nullable=False)
    public_key = Column(String, nullable=False)
    read_only = Column(Boolean, default=True)


class GPGKey(Base, GUIDPk, UserMixin, Timestamped):
    __tablename__ = "gpg_keys"
    __table_args__ = (UniqueConstraint("user_id", "gpg_key"),)
    gpg_key = Column(String, nullable=False)
    # Placeholder for compelte implementation


class DeployKey(Base, GUIDPk, RepositoryRefMixin, Timestamped):
    __tablename__ = "deploy_keys"
    __table_args__ = (UniqueConstraint("repository_id", "public_key"),)
    title = Column(String, nullable=False)
    public_key = Column(String, nullable=False)
    read_only = Column(Boolean, default=True)

    repository = relationship(Repository, back_populates="deploy_keys")


# ---------------------------------------------------------------------
# 3) Secrets
# ---------------------------------------------------------------------
class _SecretCoreMixin:  # no table, just columns
    name = Column(String(128), nullable=False)  # max 128 chars
    data = Column(String, nullable=False)  # encrypted/encoded blob
    desc = Column(String, nullable=True)  # optional free-text

    # generic input guard – tighten as needed
    __table_args__ = (CheckConstraint("length(name) > 0", name="chk_name_nonempty"),)


class UserSecret(Base, GUIDPk, _SecretCoreMixin, UserMixin, Timestamped):
    """
    One secret per (user_id, name).  Deleted when the user is deleted.
    """

    __tablename__ = "user_secrets"

    __table_args__ = (
        # scope-local uniqueness
        UniqueConstraint("user_id", "name"),
        # pull inherited constraints
        *_SecretCoreMixin.__table_args__,
    )


class OrgSecret(Base, GUIDPk, _SecretCoreMixin, OrgMixin, Timestamped):
    """
    Secret that belongs to an organisation; cascades with the org row.
    """

    __tablename__ = "org_secrets"

    __table_args__ = (
        UniqueConstraint("org_id", "name"),
        *_SecretCoreMixin.__table_args__,
    )


class RepoSecret(Base, GUIDPk, _SecretCoreMixin, RepositoryMixin, Timestamped):
    """
    Secret tied to a repository; follows repo ownership transfers & deletes.
    """

    __tablename__ = "repo_secrets"

    repository = relationship("Repository", back_populates="secrets")

    __table_args__ = (
        UniqueConstraint("repository_id", "name"),
        *_SecretCoreMixin.__table_args__,
    )


# ---------------------------------------------------------------------
# 4) Execution / queue objects (unchanged parents but FK tweaks)
# ---------------------------------------------------------------------


class Pool(Base, GUIDPk, Bootstrappable, Timestamped, TenantBound):
    __tablename__ = "pools"
    __table_args__ = (UniqueConstraint("tenant_id", "name"),)
    name = Column(String, nullable=False, unique=True)
    policy = Column(
        MutableDict.as_mutable(JSON),
        default=lambda: {"allowed_cidrs": [], "max_instances": None},
        nullable=True,
    )
    DEFAULT_ROWS = [
        {
            "id": DEFAULT_POOL_ID,
            "name": DEFAULT_POOL_NAME,
            "tenant_id": DEFAULT_TENANT_ID,
            "policy": {"allowed_cidrs": [], "max_instances": None},
        }
    ]


class Worker(Base, GUIDPk, Timestamped):
    __tablename__ = "workers"
    pool_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("pools.id"),
        nullable=False,
        default=DEFAULT_POOL_ID,
    )
    url = Column(String, nullable=False, info=dict(no_update=True))
    advertises = Column(
        MutableDict.as_mutable(JSON),  # or JSON
        default=lambda: {},  # ✔ correct for SQLAlchemy
        nullable=True,
        info=dict(no_update=True),
    )
    handlers = Column(
        MutableDict.as_mutable(JSON),  # or JSON
        default=lambda: {},  # ✔ correct for SQLAlchemy
        nullable=True,
        info=dict(no_update=True),
    )

    pool = relationship(Pool, backref="workers")


class Action(str, Enum):
    SORT = auto()
    PROCESS = auto()
    MUTATE = auto()
    EVOLVE = auto()
    FETCH = auto()
    VALIDATE = auto()


class SpecKind(str, Enum):
    DOE = "doe"  # ↦ doe_specs.id
    EVOLVE = "evolve"  # ↦ evolve_specs.id
    PAYLOAD = "payload"  # ↦ project_payloads.id


class Task(
    Base, GUIDPk, Timestamped, TenantBound, Ownable, RepositoryRefMixin, StatusMixin
):
    """Task table — explicit columns, polymorphic spec ref."""

    __tablename__ = "tasks"
    __table_args__ = ()
    # ───────── routing & ownership ──────────────────────────
    action = Column(PgEnum(Action, name="task_action"), nullable=False)
    pool_id = Column(PgUUID(as_uuid=True), ForeignKey("pools.id"), nullable=False)

    # ───────── workspace reference ──────────────────────────
    config_toml = Column(String)

    # ───────── polymorphic spec reference ───────────────────
    spec_kind = Column(PgEnum(SpecKind, name="task_spec_kind"), nullable=True)
    spec_uuid = Column(PgUUID(as_uuid=True), nullable=True)

    # (DB-level FK can’t point to multiple tables; enforce in application code.)

    # ───────── flexible metadata & labels ───────────────────
    args = Column(JSON, nullable=False, default=dict)
    labels = Column(JSON, nullable=False, default=dict)
    note = Column(String)
    schema_version = Column(Integer, nullable=False, default=3)

    works = relationship("Work", back_populates="task")  # unchanged


class Work(Base, GUIDPk, Timestamped, StatusMixin):
    """
    One execution attempt of a Task (retries generate multiple Work rows).
    """

    __tablename__ = "works"
    task_id = Column(PgUUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    result = Column(JSON, nullable=True)
    duration_s = Column(Integer)

    task = relationship(Task, back_populates="works")


# ---------------------------------------------------------------------
# 5) Raw blobs (stand-alone)
# ---------------------------------------------------------------------


class RawBlob(Base, GUIDPk, Timestamped, BlobRef):
    __tablename__ = "raw_blobs"
    mime_type = Column(String, nullable=False)
    size = Column(Integer, nullable=False)


__all__ = [
    "Tenant",
    "User",
    "Org",
    "Role",
    "RoleGrant",
    "RolePerm",
    "Status",
    "Base",
    "Repository",
    "RepositoryMixin",
    "RepositoryRefMixin",
    "UserTenant",
    "UserRepository",
    "Secret",
    "DeployKey",
    "Pool",
    "Worker",
    "Action",
    "SpecKind",
    "Task",
    "Work",
    "RawBlob",
]
