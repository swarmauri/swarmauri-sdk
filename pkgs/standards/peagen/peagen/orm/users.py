from __future__ import annotations

from autoapi.v2.tables import User as UserBase
from autoapi.v2.mixins import Bootstrappable
from autoapi.v2.mixins.upsertable import Upsertable


class User(UserBase, Bootstrappable, Upsertable):
    __upsert_keys__ = ("tenant_id", "username")
    __table_args__ = ({"extend_existing": True, "schema": "peagen"},)

__all__ = ["User"]
