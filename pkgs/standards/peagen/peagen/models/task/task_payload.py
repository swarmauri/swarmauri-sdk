"""
peagen.models.task.task_payload
===============================

Structured payload describing *what* a Task should operate on.

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

if TYPE_CHECKING:
    from ..repo.git_reference import GitReference
    from .raw_blob import RawBlob

from ..base import BaseModel


class TaskPayload(BaseModel):
    """
    Domain-level description of a Task’s inputs.

    Columns
    -------
    tenant_id       : UUID  – owning workspace
    git_reference_id: UUID? – optional FK → git_references.id
    parameters      : JSON  – arbitrary task parameters (hyper-params, etc.)
    note            : TEXT? – human note / description
    """

    __tablename__ = "task_payloads"

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
    git_reference: Mapped["GitReference | None"] = relationship(
        "GitReference", lazy="selectin"
    )

    raw_blobs: Mapped[list["RawBlob"]] = relationship(
        "RawBlob",
        back_populates="task_payload",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # ─────────────────────── Magic ───────────────────────────
    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<TaskPayload id={self.id} tenant={self.tenant_id} "
            f"git_ref={self.git_reference_id or '∅'}>"
        )
