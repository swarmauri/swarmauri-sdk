"""
peagen.models.specs.evolve_spec
===============================

Genetic / evolutionary optimisation specification.

Highlights
----------
• Scoped to a Tenant (workspace isolation).
• Optional link to a ProjectPayload (many evolve specs per project).
• Stores a semver `schema_version` and raw spec JSON.
• Enforces unique `name` within each tenant.
"""

from __future__ import annotations

import uuid
from sqlalchemy import JSON, String, Text, UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import BaseModel


class EvolveSpec(BaseModel):
    """
    Evolutionary strategy definition (population config, operators, etc.).
    """

    __tablename__ = "evolve_specs"

    # ───────────────────── Columns ─────────────────────
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )

    project_payload_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("project_payloads.id", ondelete="SET NULL"),
        nullable=True,
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
        doc="Short identifier, e.g. 'nsga2-hyperparam-search'",
    )

    schema_version: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="1.0.0",
        doc="Spec format version (semver).",
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="Optional human-readable summary of this evolution run.",
    )

    spec: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        doc="Raw JSON spec: { meta, population, operators, … }",
    )

    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_evolve_spec_per_tenant"),
    )

    # ───────────────── Relationships ───────────────────
    tenant: Mapped["Tenant"] = relationship("Tenant", lazy="selectin")

    project_payload: Mapped["ProjectPayload | None"] = relationship(
        "ProjectPayload",
        back_populates="evolve_specs",
        lazy="selectin",
    )

    # ───────────────────── Magic ───────────────────────
    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<EvolveSpec id={self.id} tenant={self.tenant_id} "
            f"name={self.name!r} version={self.schema_version}>"
        )
