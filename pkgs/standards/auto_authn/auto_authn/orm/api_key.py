"""API key model for the authentication service."""

from __future__ import annotations

from autoapi.v3.orm.tables import ApiKey as ApiKeyBase
from autoapi.v3.orm.mixins import UserColumn
from autoapi.v3.types import relationship


class ApiKey(ApiKeyBase, UserColumn):
    __table_args__ = {
        "extend_existing": True,
        "schema": "authn",
    }

    _user = relationship(
        "User",
        back_populates="_api_keys",
        lazy="joined",  # optional: eager load to avoid N+1
    )


__all__ = ["ApiKey"]
