from __future__ import annotations

from autoapi.v2.types import (
    Column,
    String,
    Text,
    JSON,
    UniqueConstraint,
    ForeignKey,
    PgUUID,
    relationship,
)
from autoapi.v2.tables import Base
from autoapi.v2.mixins import GUIDPk, Timestamped, TenantBound, Ownable

from .tenants import Tenant
from .users import User


class ProjectPayload(Base, GUIDPk, Timestamped, TenantBound, Ownable):
    __tablename__ = "project_payloads"

    tenant_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )
    doe_spec_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("doe_specs.id", ondelete="SET NULL"),
        nullable=True,
    )
    name = Column(String, nullable=False)
    schema_version = Column(String, nullable=False, default="1.0.0")
    description = Column(Text, nullable=True)
    payload = Column(JSON, nullable=False)

    __table_args__ = (UniqueConstraint("tenant_id", "name"),)

    tenant = relationship(Tenant, lazy="selectin")
    owner = relationship(User, lazy="selectin")
    doe_spec = relationship(
        "DoeSpec", back_populates="project_payloads", lazy="selectin"
    )


__all__ = ["ProjectPayload"]
