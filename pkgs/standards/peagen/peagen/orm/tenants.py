from __future__ import annotations

from autoapi.v3.tables import Tenant as TenantBase
from autoapi.v3.mixins import Bootstrappable, Upsertable
from peagen.defaults import (
    DEFAULT_TENANT_ID,
    DEFAULT_TENANT_SLUG,
)


class Tenant(TenantBase, Bootstrappable, Upsertable):
    # __mapper_args__ = {"concrete": True}
    __table_args__ = (
        {
            "extend_existing": True,
            "schema": "peagen",
        },
    )
    DEFAULT_ROWS = [
        {
            "id": DEFAULT_TENANT_ID,
            "slug": DEFAULT_TENANT_SLUG,
        }
    ]

    __upsert_keys__ = ("slug",)


__all__ = ["Tenant"]
