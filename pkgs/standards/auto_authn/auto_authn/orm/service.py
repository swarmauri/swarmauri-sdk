"""Service model for the authentication service."""

from __future__ import annotations

from autoapi.v3.tables import Base
from autoapi.v3.mixins import GUIDPk, Timestamped, TenantBound, Principal, ActiveToggle
from autoapi.v3.types import String, relationship
from autoapi.v3.specs import S, acol
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    pass


class Service(Base, GUIDPk, Timestamped, TenantBound, Principal, ActiveToggle):
    """Machine principal representing an automated service."""

    __tablename__ = "services"
    __table_args__ = ({"schema": "authn"},)
    name: str = acol(storage=S(String(120), unique=True, nullable=False))
    _service_keys = relationship(
        "auto_authn.orm.service_key.ServiceKey",
        back_populates="_service",
        cascade="all, delete-orphan",
    )


__all__ = ["Service"]
