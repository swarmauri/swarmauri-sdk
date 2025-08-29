from __future__ import annotations

from autoapi.v3.tables import Base
from autoapi.v3.types import JSON, String, Text, UniqueConstraint, Mapped, relationship
from autoapi.v3.mixins import GUIDPk, Timestamped, TenantBound, Ownable
from autoapi.v3.specs import S, acol

from .users import User


class PeagenTomlSpec(Base, GUIDPk, Timestamped, TenantBound, Ownable):
    __tablename__ = "peagen_toml_specs"
    __table_args__ = (
        UniqueConstraint("tenant_id", "name"),
        {"schema": "peagen"},
    )

    name: Mapped[str] = acol(storage=S(String, nullable=False))
    schema_version: Mapped[str] = acol(
        storage=S(String, nullable=False, default="1.0.0")
    )
    raw_toml: Mapped[str] = acol(storage=S(Text, nullable=False))
    parsed: Mapped[dict] = acol(storage=S(JSON, nullable=False, default=dict))

    owner: Mapped[User] = relationship(User, lazy="selectin")


__all__ = ["PeagenTomlSpec"]
