from __future__ import annotations

from autoapi.v2.tables import Base
from autoapi.v2.types import Column, String, UniqueConstraint, relationship
from autoapi.v2.mixins import GUIDPk, Timestamped, TenantBound, Ownable, StatusMixin


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


__all__ = ["Repository"]
