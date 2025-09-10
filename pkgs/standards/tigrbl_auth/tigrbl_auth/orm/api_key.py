"""API key model for the authentication service."""

from __future__ import annotations

from tigrbl.orm.mixins import (
    Created,
    GUIDPk,
    KeyDigest,
    LastUsed,
    UserColumn,
    ValidityWindow,
)
from tigrbl.orm.tables._base import Base
from tigrbl.specs import F, S, acol
from tigrbl.types import Mapped, String, relationship


class ApiKey(Base, GUIDPk, Created, LastUsed, ValidityWindow, UserColumn, KeyDigest):
    __tablename__ = "api_keys"
    __table_args__ = {
        "extend_existing": True,
        "schema": "authn",
    }

    label: Mapped[str] = acol(
        storage=S(String, nullable=False),
        field=F(constraints={"max_length": 120}),
    )

    _user = relationship(
        "User",
        back_populates="_api_keys",
        lazy="joined",  # optional: eager load to avoid N+1
    )


__all__ = ["ApiKey"]
