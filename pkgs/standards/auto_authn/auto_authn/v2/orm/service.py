"""Service model for the authentication service."""

from __future__ import annotations

from autoapi.v2 import Base
from autoapi.v2.mixins import GUIDPk, Timestamped, TenantBound, Principal, ActiveToggle
from autoapi.v2.types import Column, String, relationship


class Service(Base, GUIDPk, Timestamped, TenantBound, Principal, ActiveToggle):
    """Machine principal representing an automated service."""

    __tablename__ = "services"
    __table_args__ = ({"schema": "authn"},)
    name = Column(String(120), unique=True, nullable=False)
    service_keys = relationship(
        "auto_authn.v2.orm.tables.ServiceKey",
        back_populates="service",
        cascade="all, delete-orphan",
    )


__all__ = ["Service"]
