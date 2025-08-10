from __future__ import annotations

from autoapi.v2.tables import User as UserBase
from autoapi.v2.mixins import Bootstrappable
from autoapi.v2.mixins.upsertable import Upsertable


class User(UserBase, Bootstrappable, Upsertable):
    __upsert_keys__ = ("tenant_id", "username")
    __table_args__ = ({"extend_existing": True, "schema": "peagen"},)

    id = Column(
        PgUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        info=dict(
            autoapi={
                "default_factory": uuid4,
                "examples": [uuid_example],
            }
        ),
    )
    
__all__ = ["User"]
