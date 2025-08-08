from __future__ import annotations

from autoapi.v2.tables import Tenant as TenantBase
from autoapi.v2.mixins import Bootstrappable
from autoapi.v2.mixins.upsertable import Upsertable
from peagen.defaults import (
    DEFAULT_TENANT_ID,
    DEFAULT_TENANT_SLUG,
)


class Tenant(TenantBase, Bootstrappable, Upsertable):
    __upsert_keys__ = ("slug",)
    DEFAULT_ROWS = [
        {
            "id": DEFAULT_TENANT_ID,
            "slug": DEFAULT_TENANT_SLUG,
        }
    ]


__all__ = ["Tenant"]
