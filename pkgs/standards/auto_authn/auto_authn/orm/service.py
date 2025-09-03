"""Service model for the authentication service."""

from __future__ import annotations

from autoapi.v3.orm.tables import Base
from autoapi.v3.orm.mixins import (
    GUIDPk,
    Timestamped,
    TenantBound,
    Principal,
    ActiveToggle,
)
from autoapi.v3.types import Mapped, String, relationship
from autoapi.v3.specs import F, IO, S, acol, ColumnSpec
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    pass


class Service(Base, GUIDPk, Timestamped, TenantBound, Principal, ActiveToggle):
    """Machine principal representing an automated service."""

    __tablename__ = "services"
    __table_args__ = ({"schema": "authn"},)
    name: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(String(120), unique=True, nullable=False),
            field=F(constraints={"max_length": 120}, required_in=("create",)),
            io=IO(
                in_verbs=("create", "update", "replace"),
                out_verbs=("read", "list"),
                filter_ops=("eq", "ilike"),
                sortable=True,
            ),
        )
    )
    _service_keys = relationship(
        "ServiceKey",
        back_populates="_service",
        cascade="all, delete-orphan",
    )


__all__ = ["Service"]
