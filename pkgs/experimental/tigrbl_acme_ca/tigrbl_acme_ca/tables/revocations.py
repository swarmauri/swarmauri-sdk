from __future__ import annotations

import datetime as dt

from tigrbl.orm.tables import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.specs import acol, IO, F, S, ColumnSpec
from tigrbl.column.storage_spec import ForeignKeySpec
from tigrbl.types import (
    PgUUID,
    UUID as UUIDType,
    String,
    TZDateTime,
)


class Revocation(Base, GUIDPk):
    __tablename__ = "acme_revocations"
    __resource__ = "revocation"

    certificate_id = acol(
        spec=ColumnSpec(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(target="acme_certificates.id"),
                nullable=False,
                index=True,
            ),
            field=F(py_type=UUIDType),
            io=IO(in_verbs=("create",), out_verbs=("read", "list")),
        )
    )
    reason = acol(
        spec=ColumnSpec(
            storage=S(type_=String(64), nullable=True),
            field=F(py_type=str, allow_null_in=("create",)),
            io=IO(in_verbs=("create",), out_verbs=("read", "list")),
        )
    )
    revoked_at = acol(
        spec=ColumnSpec(
            storage=S(
                type_=TZDateTime,
                nullable=False,
                default=lambda: dt.datetime.now(dt.timezone.utc),
            ),
            field=F(py_type=dt.datetime),
            io=IO(in_verbs=("create",), out_verbs=("read", "list")),
        )
    )
