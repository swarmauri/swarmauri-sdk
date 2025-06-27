"""
peagen.models.repo.repository
=============================

SQLAlchemy ORM model for a Git repository tracked by Peagen.

Key Design Points
-----------------
• Each repository **belongs to one Tenant** (workspace).
• Name uniqueness is enforced **within** its tenant.
• Relationships:
    Tenant ▸ Repository        (many-to-one)
    Repository ▸ GitReference  (one-to-many)
    Repository ▸ DeployKey     (one-to-many)
    Repository ▸ RepositoryUserAssociation (one-to-many → user ACL / role)
"""

from __future__ import annotations

import uuid
from sqlalchemy import String, UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - imports for type hints
    from ..tenant.tenant import Tenant
    from .git_reference import GitReference
    from .repository_deploy_key_association import RepositoryDeployKeyAssociation
    from .deploy_key import DeployKey
    from .repository_user_association import RepositoryUserAssociation
    from ..config.peagen_toml_spec import PeagenTomlSpec

# Import at runtime so SQLAlchemy can resolve relationship targets

from ..base import BaseModel


class Repository(BaseModel):
    """
    Represents a Git repository mirrored or managed by Peagen.
    """

    __tablename__ = "repositories"

    # ──────────────────────── Columns ────────────────────────
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)  # logical repo name
    url: Mapped[str] = mapped_column(
        String, nullable=False
    )  # canonical remote URL (Gitea / GitHub)
    description: Mapped[str] = mapped_column(
        String, nullable=True
    )  # optional human description
    default_branch: Mapped[str] = mapped_column(String, nullable=True)  # e.g. "main"

    # Enforce unique repo names *within* each tenant
    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_repository_per_tenant"),
    )

    # ──────────────────── Relationships ──────────────────────
    tenant: Mapped["Tenant"] = relationship(
        "Tenant", lazy="selectin", back_populates="repositories"
    )

    git_references: Mapped[list["GitReference"]] = relationship(
        "GitReference",
        back_populates="repository",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    deploy_key_associations: Mapped[list["RepositoryDeployKeyAssociation"]] = (
        relationship(
            "RepositoryDeployKeyAssociation",
            back_populates="repository",
            cascade="all, delete-orphan",
            lazy="selectin",
        )
    )

    toml_specs: Mapped[list["PeagenTomlSpec"]] = relationship(
        "PeagenTomlSpec",
        back_populates="repository",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    deploy_keys: Mapped[list["DeployKey"]] = relationship(
        "DeployKey",
        secondary="repository_deploy_key_associations",
        back_populates="repositories",
        lazy="selectin",
    )

    user_associations: Mapped[list["RepositoryUserAssociation"]] = relationship(
        "RepositoryUserAssociation",
        back_populates="repository",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # ─────────────────────── Magic ───────────────────────────
    def __repr__(self) -> str:  # pragma: no cover
        return f"<Repository tenant_id={self.tenant_id} name={self.name!r}>"
