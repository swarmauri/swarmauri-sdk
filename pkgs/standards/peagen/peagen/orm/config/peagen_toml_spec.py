"""
peagen.orm.config.peagen_toml_spec
=====================================

Canonical record of a `.peagen.toml` file.

Design Highlights
-----------------
• **Tenant-scoped** — every config belongs to exactly one workspace.
• **Optional repository link** — when the TOML came from a specific repo.
• Stores both the *raw* TOML text and a *parsed* JSON representation.
• Versioned via `schema_version` (semver of the TOML spec).
• (`tenant_id`, `name`) pair is unique.
"""

from __future__ import annotations

import uuid
from sqlalchemy import JSON, String, Text, UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..repo.repository import RepositoryModel
from ..tenant.tenant import TenantModel

from ..base import BaseModel


class PeagenTomlSpecModel(BaseModel):
    """
    Parsed & raw representation of a `.peagen.toml` file.
    """

    __tablename__ = "peagen_toml_specs"

    # ───────────────────── Columns ─────────────────────
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )

    repository_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="SET NULL"),
        nullable=True,
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
        doc="Logical identifier, e.g. 'default-build', unique per tenant.",
    )

    schema_version: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="1.0.0",
        doc="TOML spec version (semver).",
    )

    raw_toml: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Exact TOML string as committed.",
    )

    parsed: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        doc="Canonical JSON form produced by TOML parser.",
        default=dict,
    )

    __table_args__ = (UniqueConstraint("tenant_id", "name", name="uq_toml_per_tenant"),)

    # ───────────────── Relationships ───────────────────
    tenant: Mapped["TenantModel"] = relationship("TenantModel", lazy="selectin")

    repository: Mapped[RepositoryModel | None] = relationship(
        "RepositoryModel",
        lazy="selectin",
        back_populates="toml_specs",
    )

    # ───────────────────── Magic ───────────────────────
    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<PeagenTomlSpec id={self.id} tenant={self.tenant_id} "
            f"name={self.name!r} version={self.schema_version}>"
        )


PeagenTomlSpec = PeagenTomlSpecModel
