"""Service key model for the authentication service."""

from __future__ import annotations

from autoapi.v2.tables import ApiKey as ApiKeyBase
from autoapi.v2.types import Column, ForeignKey, PgUUID, UniqueConstraint, relationship


class ServiceKey(ApiKeyBase):
    __tablename__ = "service_keys"
    __table_args__ = (
        UniqueConstraint("digest"),
        {"extend_existing": True, "schema": "authn"},
    )
    service_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("authn.services.id"),
        index=True,
        nullable=False,
    )

    service = relationship(
        "auto_authn.v2.orm.tables.Service",
        back_populates="service_keys",
        lazy="joined",
    )


__all__ = ["ServiceKey"]
