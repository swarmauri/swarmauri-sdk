"""Tenant model for the authentication service."""

from __future__ import annotations

import uuid

from autoapi.v3.tables import Tenant as TenantBase
from autoapi.v3.mixins import Bootstrappable
from autoapi.v3.specs import acol, S
from autoapi.v3.types import Mapped, String


class Tenant(TenantBase, Bootstrappable):
    __table_args__ = (
        {
            "extend_existing": True,
            "schema": "authn",
        },
    )
    name: Mapped[str] = acol(storage=S(String, nullable=False, unique=True))
    email: Mapped[str] = acol(storage=S(String, nullable=False, unique=True))
    DEFAULT_ROWS = [
        {
            "id": uuid.UUID("FFFFFFFF-0000-0000-0000-000000000000"),
            "email": "tenant@example.com",
            "name": "Public",
            "slug": "public",
        }
    ]


__all__ = ["Tenant"]
