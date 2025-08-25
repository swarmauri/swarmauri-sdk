"""Tenant model for the authentication service."""

from __future__ import annotations

import uuid

from autoapi.v2.tables import Tenant as TenantBase
from autoapi.v2.types import Column, String
from autoapi.v2.mixins import Bootstrappable


class Tenant(TenantBase, Bootstrappable):
    __table_args__ = (
        {
            "extend_existing": True,
            "schema": "authn",
        },
    )
    name = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    DEFAULT_ROWS = [
        {
            "id": uuid.UUID("FFFFFFFF-0000-0000-0000-000000000000"),
            "email": "tenant@example.com",
            "name": "Public",
            "slug": "public",
        }
    ]


__all__ = ["Tenant"]
