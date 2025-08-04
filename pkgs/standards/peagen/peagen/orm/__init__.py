"""
peagen/orm/__init__.py  –  all Peagen domain tables in one place
(uses only sqlalchemy.Column – no mapped_column / JSONB).
"""

from __future__ import annotations

from typing import FrozenSet

from autoapi.v2.types import (
    Column,
    Integer,
    String,
    UniqueConstraint,
    relationship,
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
    Ownable,
    Bootstrappable,
    Timestamped,
    TenantBound,
    StatusMixin,
    BlobRef,
)

from .pools import Pool
from .workers import Worker
from .keys import PublicKey, GPGKey, DeployKey
from .secrets import UserSecret, OrgSecret, RepoSecret
from .tasks import Action, SpecKind, Task
from .works import Work
from .mixins import RepositoryMixin, RepositoryRefMixin


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
    DEFAULT_ROWS = [
        {
            "id": DEFAULT_TENANT_ID,
            "email": DEFAULT_TENANT_EMAIL,
            "name": DEFAULT_TENANT_NAME,
            "slug": DEFAULT_TENANT_SLUG,
        }
    ]


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
    "UserRepository",
    "PublicKey",
    "GPGKey",
    "DeployKey",
    "UserSecret",
    "OrgSecret",
    "RepoSecret",
    "Pool",
    "Worker",
    "Action",
    "SpecKind",
    "Task",
    "Work",
    "RawBlob",
]
