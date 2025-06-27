"""
peagen.orm.task.task
=======================

Structured payload describing *what* a task should operate on.

Key Features
------------
• Belongs to a Tenant  (multi-workspace isolation).
• Optionally anchors to a GitReference  (code/data version).
• Can embed an arbitrary JSON `parameters` blob.
• One-to-many attachment of RawBlob objects (binary / large inputs).
"""

from __future__ import annotations

import uuid
from sqlalchemy import JSON, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - imports for type hints
    from ..repo.git_reference import GitReferenceModel
    from .raw_blob import RawBlobModel

from ..repo.git_reference import GitReferenceModel
from ..base import BaseModel


class TaskModel(BaseModel):
    """
    Domain-level description of a Task’s inputs.

    Columns
    -------
    tenant_id       : UUID  – owning workspace
    git_reference_id: UUID? – optional FK → git_references.id
    parameters      : JSON  – arbitrary task parameters (hyper-params, etc.)
    note            : TEXT? – human note / description
    """

    __tablename__ = "tasks"

    # ──────────────────────── Columns ────────────────────────
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )

    git_reference_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("git_references.id", ondelete="SET NULL"),
        nullable=True,
    )

    parameters: Mapped[dict] = mapped_column(
        JSON, nullable=False, default=dict, doc="Arbitrary JSON parameters"
    )

    note: Mapped[str | None] = mapped_column(
        Text, nullable=True, doc="Optional human description"
    )

    # ──────────────────── Relationships ──────────────────────
    git_reference: Mapped[GitReferenceModel | None] = relationship(
        "GitReferenceModel", lazy="selectin"
    )

    raw_blobs: Mapped[list["RawBlobModel"]] = relationship(
        "RawBlobModel",
        back_populates="task",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # ─────────────────────── Magic ───────────────────────────
    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<Task id={self.id} tenant={self.tenant_id} "
            f"git_ref={self.git_reference_id or '∅'}>"
        )


Task = TaskModel
