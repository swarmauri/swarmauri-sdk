"""
peagen.models.infra.pool_worker_association
==========================================

Join table linking Workers to Pools.

• A worker may belong to multiple pools (multi-queue scheduling).
• A pool may host many workers.
• `status` column allows you to temporarily disable a worker for a pool
  without removing the association row.
"""

from __future__ import annotations

import enum
import uuid
from sqlalchemy import Enum, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - imports for type hints
    from .pool import Pool
    from .worker import Worker

from ..base import BaseModel


# ────────────────────────── Status Enum ──────────────────────────
class PoolWorkerStatus(str, enum.Enum):
    active = "active"
    disabled = "disabled"


# ───────────────────────── Association ───────────────────────────
class PoolWorkerAssociationModel(BaseModel):
    """
    Maps a Worker to a Pool with an optional status.
    """

    __tablename__ = "pool_worker_associations"

    # ─────────────────── Columns ──────────────────
    pool_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pools.id", ondelete="CASCADE"),
        nullable=False,
    )

    worker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workers.id", ondelete="CASCADE"),
        nullable=False,
    )

    status: Mapped[PoolWorkerStatus] = mapped_column(
        Enum(PoolWorkerStatus, name="pool_worker_status_enum"),
        nullable=False,
        default=PoolWorkerStatus.active,
    )

    __table_args__ = (UniqueConstraint("pool_id", "worker_id", name="uq_pool_worker"),)

    # ───────────── Relationships ────────────────
    pool: Mapped["Pool"] = relationship(
        "Pool",
        back_populates="worker_associations",
        lazy="selectin",
    )

    worker: Mapped["Worker"] = relationship(
        "Worker",
        back_populates="pool_associations",
        lazy="selectin",
    )

    # ───────────────── Magic ─────────────────────
    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<PoolWorkerAssociation pool={self.pool_id} "
            f"worker={self.worker_id} status={self.status}>"
        )


PoolWorkerAssociation = PoolWorkerAssociationModel
