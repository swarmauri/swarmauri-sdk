"""API key model for the authentication service."""

from __future__ import annotations

from autoapi.v2.tables import ApiKey as ApiKeyBase
from autoapi.v2.types import UniqueConstraint, relationship
from autoapi.v2.mixins import UserMixin


class ApiKey(ApiKeyBase, UserMixin):
    __table_args__ = (
        UniqueConstraint("digest"),
        {"extend_existing": True, "schema": "authn"},
    )

    user = relationship(
        "auto_authn.v2.orm.tables.User",
        back_populates="api_keys",
        lazy="joined",  # optional: eager load to avoid N+1
    )


__all__ = ["ApiKey"]
