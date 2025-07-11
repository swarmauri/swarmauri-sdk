# domain_models.py
"""
All Peagen domain tables in one place,
now with every table Ownable (i.e. has owner_id FK to users.id)
and properly named unique constraints.
"""

from __future__ import annotations

from autoapi.v2.types import (
    Column,
    String,
    Text,
    JSON,
    UniqueConstraint,
    ForeignKey,
    UUID,
    relationship
)

from autoapi.v2.tables import Base, Tenant, User
from autoapi.v2.mixins import (
    GUIDPk,
    Timestamped,
    TenantBound,
    Ownable,
)

# ────────────────────────────────────────────────────────────────────────
class DoeSpec(Base, GUIDPk, Timestamped, TenantBound, Ownable):
    __tablename__ = "doe_specs"

    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String, nullable=False)
    schema_version = Column(String, nullable=False, default="1.1.0")
    description = Column(Text, nullable=True)
    spec = Column(JSON, nullable=False)

    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_doe_specs_tenant_name"),
    )

    tenant = relationship(Tenant, lazy="selectin")
    owner = relationship(User, lazy="selectin")
    project_payloads = relationship(
        "ProjectPayload",
        back_populates="doe_spec",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class EvolveSpec(Base, GUIDPk, Timestamped, TenantBound, Ownable):
    __tablename__ = "evolve_specs"

    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String, nullable=False)
    schema_version = Column(String, nullable=False, default="1.0.0")
    description = Column(Text, nullable=True)
    spec = Column(JSON, nullable=False)

    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_evolve_specs_tenant_name"),
    )

    tenant = relationship(Tenant, lazy="selectin")
    owner = relationship(User, lazy="selectin")


class ProjectPayload(Base, GUIDPk, Timestamped, TenantBound, Ownable):
    __tablename__ = "project_payloads"

    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    doe_spec_id = Column(
        UUID(as_uuid=True),
        ForeignKey("doe_specs.id", ondelete="SET NULL"),
        nullable=True,
    )
    name = Column(String, nullable=False)
    schema_version = Column(String, nullable=False, default="1.0.0")
    description = Column(Text, nullable=True)
    payload = Column(JSON, nullable=False)

    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_project_payloads_tenant_name"),
    )

    tenant = relationship(Tenant, lazy="selectin")
    owner = relationship(User, lazy="selectin")
    doe_spec = relationship(
        "DoeSpec", back_populates="project_payloads", lazy="selectin"
    )


class PeagenTomlSpec(Base, GUIDPk, Timestamped, TenantBound, Ownable):
    __tablename__ = "peagen_toml_specs"

    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    repository_id = Column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="SET NULL"),
        nullable=True,
    )
    name = Column(String, nullable=False)
    schema_version = Column(String, nullable=False, default="1.0.0")
    raw_toml = Column(Text, nullable=False)
    parsed = Column(JSON, nullable=False, default=dict)

    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_peagen_toml_specs_tenant_name"),
    )

    tenant = relationship(Tenant, lazy="selectin")
    owner = relationship(User, lazy="selectin")


class EvalResult(Base, GUIDPk, Timestamped, Ownable):
    __tablename__ = "eval_results"
    work_id = Column(UUID(as_uuid=True), ForeignKey("works.id", ondelete="CASCADE"))
    label   = Column(String)
    metrics = Column(JSON, nullable=False)
    owner   = relationship(User, lazy="selectin")
    work    = relationship("Work", back_populates="eval_results", lazy="selectin")
    analyses = relationship(
        "AnalysisResult",
        back_populates="eval_result",
        cascade="all, delete-orphan",
        lazy="selectin",
    )



class AnalysisResult(Base, GUIDPk, Timestamped, Ownable):
    __tablename__ = "analysis_results"
    eval_result_id = Column(
        UUID(as_uuid=True), ForeignKey("eval_results.id", ondelete="CASCADE")
    )
    summary = Column(Text)
    data    = Column(JSON, default=dict, nullable=False)
    owner   = relationship(User, lazy="selectin")
    eval_result = relationship("EvalResult", back_populates="analyses", lazy="selectin")

