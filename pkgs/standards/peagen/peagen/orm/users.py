from __future__ import annotations

from tigrbl.orm.tables import User as UserBase
from tigrbl.orm.mixins import Bootstrappable, Upsertable, uuid_example
from tigrbl.types import PgUUID, Mapped, uuid4
from tigrbl.specs import S, F, acol


class User(UserBase, Bootstrappable, Upsertable):
    __table_args__ = ({"extend_existing": True, "schema": "peagen"},)

    id: Mapped[PgUUID] = acol(
        storage=S(PgUUID(as_uuid=True), primary_key=True, default=uuid4),
        field=F(constraints={"examples": [uuid_example]}),
    )


__all__ = ["User"]
