"""
peagen.models.specs.project_payload
===================================

High-level container describing a *Project*—the umbrella under which DOE and
Evolve specifications, datasets, packages, and resources live.

Design Principles
-----------------
• **Tenant-scoped**: multiple projects per workspace.
• **Versioned**: carries its own `schema_version` (semver).
• **Flexible**: stores the raw JSON payload exactly as supplied.
• **Hub**: provides back-references to DoeSpec and EvolveSpec.

Table-level guarantees
----------------------
• (`tenant_id`, `name`) pair is unique.
• Deleting the Project cascades to its DOE / Evolve specs.
"""

from __future__ import annotations

import uuid
from sqlalchemy import JSON, String, Text, UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import BaseModel


class ProjectPayload(BaseModel):
    """
    A workspace-level project definition (packages, datasets, resources …).
    """

    __tablename__ = "project_payloads"

    # ───────────────────── Columns ─────────────────────
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
        doc="Human-friendly project identifier, unique per tenant.",
    )

    schema_version: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="1.0.0",
        doc="Schema format version (semver).",
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="Optional narrative description of the project.",
    )

    payload: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        doc="Raw project JSON (PROJECTS, PACKAGES, DATASETS, …).",
    )

    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_project_per_tenant"),
    )

    # ───────────────── Relationships ───────────────────
    tenant: Mapped["Tenant"] = relationship("Tenant", lazy="selectin")

    doe_specs: Mapped[list["DoeSpec"]] = relationship(
        "DoeSpec",
        back_populates="project_payload",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    evolve_specs: Mapped[list["EvolveSpec"]] = relationship(
        "EvolveSpec",
        back_populates="project_payload",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # ───────────────────── Magic ───────────────────────
    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<ProjectPayload id={self.id} tenant={self.tenant_id} "
            f"name={self.name!r} version={self.schema_version}>"
        )
