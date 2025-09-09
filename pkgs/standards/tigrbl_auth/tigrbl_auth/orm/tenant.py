"""Tenant model for the authentication service."""

from __future__ import annotations

import uuid

from tigrbl.v3.orm.tables import Tenant as TenantBase
from tigrbl.v3.orm.mixins import Bootstrappable
from tigrbl.v3.specs import F, IO, S, acol, ColumnSpec
from tigrbl.v3.types import Mapped, String


class Tenant(TenantBase, Bootstrappable):
    __table_args__ = (
        {
            "extend_existing": True,
            "schema": "authn",
        },
    )
    name: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(String, nullable=False, unique=True),
            field=F(constraints={"max_length": 120}, required_in=("create",)),
            io=IO(
                in_verbs=("create", "update", "replace"),
                out_verbs=("read", "list"),
                filter_ops=("eq", "ilike"),
                sortable=True,
            ),
        )
    )
    email: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(String, nullable=False, unique=True),
            field=F(constraints={"max_length": 120}, required_in=("create",)),
            io=IO(
                in_verbs=("create", "update", "replace"),
                out_verbs=("read", "list"),
                filter_ops=("eq", "ilike"),
                sortable=True,
            ),
        )
    )
    DEFAULT_ROWS = [
        {
            "id": uuid.UUID("FFFFFFFF-0000-0000-0000-000000000000"),
            "email": "tenant@example.com",
            "name": "Public",
            "slug": "public",
        }
    ]


__all__ = ["Tenant"]
