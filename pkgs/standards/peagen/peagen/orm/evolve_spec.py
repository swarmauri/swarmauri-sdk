from __future__ import annotations

from autoapi.v3.types import (
    Column,
    String,
    Text,
    JSON,
    UniqueConstraint,
    relationship,
)
from autoapi.v3.tables import Base
from autoapi.v3.mixins import GUIDPk, Timestamped, TenantBound, Ownable

from .users import User


class EvolveSpec(Base, GUIDPk, Timestamped, TenantBound, Ownable):
    __tablename__ = "evolve_specs"
    __table_args__ = (
        UniqueConstraint("tenant_id", "name"),
        {"schema": "peagen"},
    )
    name = Column(String, nullable=False)
    schema_version = Column(String, nullable=False, default="1.0.0")
    description = Column(Text, nullable=True)
    spec = Column(JSON, nullable=False)

    owner = relationship(User, lazy="selectin")


__all__ = ["EvolveSpec"]
