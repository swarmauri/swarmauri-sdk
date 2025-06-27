"""
peagen.models.infra.pool
========================

A logical pool of workers with a shared scheduling or resource policy.

Key Points
----------
• Tenant-scoped – multiple pools per workspace.
• `name` is unique within its tenant.
• Holds simple operational metadata (`policy`, `capacity`, `description`).
• Relationship to Worker via PoolWorkerAssociation.
"""

from __future__ import annotations

import uuid
from sqlalchemy import JSON, String, Text, UniqueConstraint, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - imports for type hints
    from ..tenant.tenant import Tenant
    from .pool_worker_association import PoolWorkerAssociation
    from .worker import Worker

from ..base import BaseModel


class PoolModel(BaseModel):
    """
    Compute / execution pool definition.
    """

    __tablename__ = "pools"

    # ───────────────────── Columns ─────────────────────
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
        doc="Unique pool name inside a tenant.",
    )

    capacity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Maximum concurrent workers (0 = unlimited).",
    )

    policy: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        doc="Arbitrary JSON scheduling / scaling policy.",
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="Optional human-readable description.",
    )

    __table_args__ = (UniqueConstraint("tenant_id", "name", name="uq_pool_per_tenant"),)

    # ───────────────── Relationships ───────────────────
    tenant: Mapped["Tenant"] = relationship("Tenant", lazy="selectin")

    worker_associations: Mapped[list["PoolWorkerAssociation"]] = relationship(
        "PoolWorkerAssociation",
        back_populates="pool",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    workers: Mapped[list["Worker"]] = relationship(
        "Worker",
        secondary="pool_worker_associations",
        viewonly=True,
        lazy="selectin",
    )

    # ───────────────────── Magic ───────────────────────
    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<Pool id={self.id} tenant={self.tenant_id} "
            f"name={self.name!r} capacity={self.capacity}>"
        )


Pool = PoolModel
