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


class PeagenTomlSpec(Base, GUIDPk, Timestamped, TenantBound, Ownable):
    __tablename__ = "peagen_toml_specs"

    tenant_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )
    repository_id = Column(
        PgUUID(as_uuid=True),
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


__all__ = ["PeagenTomlSpec"]
