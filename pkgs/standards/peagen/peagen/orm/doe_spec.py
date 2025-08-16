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


class DoeSpec(Base, GUIDPk, Timestamped, TenantBound, Ownable):
    __tablename__ = "doe_specs"
    __table_args__= (UniqueConstraint("tenant_id", "name"), {"schema": "peagen"},)

 
    name = Column(String, nullable=False)
    schema_version = Column(String, nullable=False, default="1.1.0")
    description = Column(Text, nullable=True)
    spec = Column(JSON, nullable=False)

    owner = relationship(User, lazy="selectin")
    project_payloads = relationship(
        "ProjectPayload",
        back_populates="doe_spec",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


__all__ = ["DoeSpec"]
