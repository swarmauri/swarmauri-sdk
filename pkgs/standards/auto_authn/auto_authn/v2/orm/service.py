"""Service model for the authentication service."""

from __future__ import annotations

from autoapi.v3.tables import Base
from autoapi.v3.mixins import GUIDPk, Timestamped, TenantBound, Principal, ActiveToggle
from autoapi.v3.types import String, relationship
from autoapi.v3.specs import IO, S, acol, vcol
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .service_key import ServiceKey


class Service(Base, GUIDPk, Timestamped, TenantBound, Principal, ActiveToggle):
    """Machine principal representing an automated service."""

    __tablename__ = "services"
    __table_args__ = ({"schema": "authn"},)
    name: str = acol(storage=S(String(120), unique=True, nullable=False))
    _service_keys = relationship(
        "auto_authn.v2.orm.tables.ServiceKey",
        back_populates="_service",
        cascade="all, delete-orphan",
    )
    service_keys: list["ServiceKey"] = vcol(
        read_producer=lambda obj, _ctx: obj._service_keys,
        io=IO(out_verbs=("read", "list")),
    )


__all__ = ["Service"]
