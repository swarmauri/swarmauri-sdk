"""
peagen.orm.repo.repository_deploy_key_association
===================================================

Join table linking DeployKeys to Repositories.

Each deploy key belongs to a user and may be attached to many repositories via
this association table.
"""

from __future__ import annotations

import uuid
from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - imports for type hints
    from .repository import RepositoryModel
    from .deploy_key import DeployKeyModel

from ..base import BaseModel


class RepositoryDeployKeyAssociationModel(BaseModel):
    """Associates a deploy key with a repository."""

    __tablename__ = "repository_deploy_key_associations"

    # ----------------------------- Columns -----------------------------
    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
    )
    deploy_key_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("deploy_keys.id", ondelete="CASCADE"),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "repository_id",
            "deploy_key_id",
            name="uq_repository_deploy_key",
        ),
    )

    # --------------------------- Relationships ---------------------------
    repository: Mapped["RepositoryModel"] = relationship(
        "RepositoryModel", back_populates="deploy_key_associations", lazy="selectin"
    )
    deploy_key: Mapped["DeployKeyModel"] = relationship(
        "DeployKeyModel", back_populates="repository_associations", lazy="selectin"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<RepositoryDeployKeyAssociation repo={self.repository_id} key={self.deploy_key_id}>"
