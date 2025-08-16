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


class PeagenTomlSpec(Base, GUIDPk, Timestamped, TenantBound, Ownable):
    __tablename__ = "peagen_toml_specs"
    __table_args__ = (
        UniqueConstraint("tenant_id", "name"),
        {"schema": "peagen"},
    )

    name = Column(String, nullable=False)
    schema_version = Column(String, nullable=False, default="1.0.0")
    raw_toml = Column(Text, nullable=False)
    parsed = Column(JSON, nullable=False, default=dict)

    owner = relationship(User, lazy="selectin")


__all__ = ["PeagenTomlSpec"]
