"""
peagen.models.infra.worker
==========================

A physical or virtual machine / container that can execute TaskRuns.

Design Objectives
-----------------
• **Tenant-scoped** – a worker belongs to a single workspace for security
  segmentation; if you later want global workers, remove `tenant_id`.
• **Many–to–many** with Pool via PoolWorkerAssociation.
• Tracks lightweight runtime telemetry (`status`, `last_heartbeat`,
  optional JSON `metrics`).

Status Life-cycle
-----------------
`idle` → `reserved` → `running` → `offline` (heartbeat lost)
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Enum, ForeignKey, String, TIMESTAMP, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - imports for type hints
    from ..tenant.tenant import Tenant
    from .pool_worker_association import PoolWorkerAssociation
    from .pool import Pool
    from ..task.task_run import TaskRun

from ..base import BaseModel


# ────────────────────────── Status Enum ──────────────────────────
class WorkerStatus(str, enum.Enum):
    idle = "idle"
    reserved = "reserved"
    running = "running"
    offline = "offline"


# ──────────────────────────── Model ─────────────────────────────
class WorkerModel(BaseModel):
    """
    Execution agent capable of processing tasks.
    """

    __tablename__ = "workers"

    # ─────────────────── Columns ──────────────────
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
        doc="Logical worker name (e.g., 'gpu-node-7').",
    )

    hostname: Mapped[str] = mapped_column(
        String,
        nullable=False,
        doc="Underlying host/container name; used for SSH / monitoring.",
    )

    status: Mapped[WorkerStatus] = mapped_column(
        Enum(WorkerStatus, name="worker_status_enum"),
        nullable=False,
        default=WorkerStatus.idle,
    )

    last_heartbeat: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    metrics: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        doc="Optional runtime metrics snapshot (CPU, GPU, mem …).",
    )

    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_worker_per_tenant"),
    )

    # ─────────────── Relationships ────────────────
    tenant: Mapped["Tenant"] = relationship("Tenant", lazy="selectin")

    pool_associations: Mapped[list["PoolWorkerAssociation"]] = relationship(
        "PoolWorkerAssociation",
        back_populates="worker",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    pools: Mapped[list["Pool"]] = relationship(
        "Pool",
        secondary="pool_worker_associations",
        viewonly=True,
        lazy="selectin",
    )

    task_runs: Mapped[list["TaskRun"]] = relationship(
        "TaskRun",
        back_populates="worker",
        lazy="selectin",
    )

    # ─────────────────── Magic ────────────────────
    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<Worker id={self.id} tenant={self.tenant_id} "
            f"name={self.name!r} status={self.status}>"
        )


Worker = WorkerModel
