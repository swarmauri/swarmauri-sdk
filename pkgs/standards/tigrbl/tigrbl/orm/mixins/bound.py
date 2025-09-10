from __future__ import annotations

from ...config.constants import CTX_AUTH_KEY, CTX_USER_ID_KEY
from ...specs import ColumnSpec, F, S, acol
from ...specs.storage_spec import ForeignKeySpec
from ...types import PgUUID, UUID, Mapped

from .utils import uuid_example, CRUD_IO


class OwnerBound:
    owner_id: Mapped[UUID] = acol(
        spec=ColumnSpec(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(target="users.id"),
            ),
            field=F(py_type=UUID, constraints={"examples": [uuid_example]}),
            io=CRUD_IO,
        )
    )

    @classmethod
    def filter_for_ctx(cls, q, ctx):
        auto_fields = ctx.get(CTX_AUTH_KEY, {})
        return q.filter(cls.owner_id == auto_fields.get(CTX_USER_ID_KEY))


class UserBound:
    user_id: Mapped[UUID] = acol(
        spec=ColumnSpec(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(target="users.id"),
            ),
            field=F(py_type=UUID, constraints={"examples": [uuid_example]}),
            io=CRUD_IO,
        )
    )

    @classmethod
    def filter_for_ctx(cls, q, ctx):
        auto_fields = ctx.get(CTX_AUTH_KEY, {})
        return q.filter(cls.user_id == auto_fields.get(CTX_USER_ID_KEY))


__all__ = ["OwnerBound", "UserBound"]
