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


class EvolveSpec(Base, GUIDPk, Timestamped, TenantBound, Ownable):
    __tablename__ = "evolve_specs"

    tenant_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(String, nullable=False)
    schema_version = Column(String, nullable=False, default="1.0.0")
    description = Column(Text, nullable=True)
    spec = Column(JSON, nullable=False)

    __table_args__ = (UniqueConstraint("tenant_id", "name"),)

    tenant = relationship(Tenant, lazy="selectin")
    owner = relationship(User, lazy="selectin")


__all__ = ["EvolveSpec"]
