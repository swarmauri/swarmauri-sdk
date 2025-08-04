from __future__ import annotations

from autoapi.v2.tables import Tenant as TenantBase
from autoapi.v2.mixins import Bootstrappable
from peagen.defaults import (
    DEFAULT_TENANT_ID,
    DEFAULT_TENANT_EMAIL,
    DEFAULT_TENANT_NAME,
    DEFAULT_TENANT_SLUG,
)


class Tenant(TenantBase, Bootstrappable):
    DEFAULT_ROWS = [
        {
            "id": DEFAULT_TENANT_ID,
            "email": DEFAULT_TENANT_EMAIL,
            "name": DEFAULT_TENANT_NAME,
            "slug": DEFAULT_TENANT_SLUG,
        }
    ]


__all__ = ["Tenant"]
