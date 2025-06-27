"""
peagen.models.specs.doe_spec
============================

Design-of-Experiments (DOE) specification.

Key Features
------------
• Scoped to a Tenant  (multi-workspace isolation).
• Can produce multiple ProjectPayloads.
• Stores a semantic version tag (`schema_version`) and the raw spec JSON.
• Uniqueness: DOE spec `name` must be unique **within** its tenant.
"""

from __future__ import annotations

import uuid
from sqlalchemy import JSON, String, Text, UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..tenant.tenant import Tenant
    from .project_payload import ProjectPayload

from ..base import BaseModel


class DoeSpec(BaseModel):
    """
    A Design-of-Experiments definition (factor levels, ranges, or sampling plan).
    """

    __tablename__ = "doe_specs"

    # ───────────────────── Columns ─────────────────────
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
        doc="Short identifier, e.g. 'augmentation-grid'",
    )

    schema_version: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="1.1.0",
        doc="Spec format version (semver).",
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="Optional human-readable summary.",
    )

    spec: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        doc="Raw DOE JSON (FACTORS, patches, etc.).",
    )

    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_doe_spec_per_tenant"),
    )

    # ───────────────── Relationships ───────────────────
    tenant: Mapped["Tenant"] = relationship("Tenant", lazy="selectin")

    project_payloads: Mapped[list["ProjectPayload"]] = relationship(
        "ProjectPayload",
        back_populates="doe_spec",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # ───────────────────── Magic ───────────────────────
    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<DoeSpec id={self.id} tenant={self.tenant_id} "
            f"name={self.name!r} version={self.schema_version}>"
        )
