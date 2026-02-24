from __future__ import annotations

import datetime as dt

from tigrbl.orm.tables import Base
from tigrbl.orm.mixins import GUIDPk, Timestamped
from tigrbl.specs import acol, IO, F, S, ColumnSpec
from tigrbl.column.storage_spec import ForeignKeySpec
from tigrbl.types import (
    PgUUID,
    UUID as UUIDType,
    String,
    Boolean,
    TZDateTime,
)


class Authorization(Base, GUIDPk, Timestamped):
    __tablename__ = "acme_authorizations"
    __resource__ = "authorization"

    order_id = acol(
        spec=ColumnSpec(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(target="acme_orders.id"),
                nullable=False,
                index=True,
            ),
            field=F(py_type=UUIDType),
            io=IO(in_verbs=("create",), out_verbs=("read", "list")),
        )
    )
    identifier = acol(
        spec=ColumnSpec(
            storage=S(type_=String(255), nullable=False, index=True),
            field=F(py_type=str),
            io=IO(in_verbs=("create",), out_verbs=("read", "list"), sortable=True),
        )
    )
    status = acol(
        spec=ColumnSpec(
            storage=S(type_=String(24), nullable=False, default="pending"),
            field=F(py_type=str, examples=["pending", "valid", "invalid", "expired"]),
            io=IO(in_verbs=("update",), out_verbs=("read", "list")),
        )
    )
    expires_at = acol(
        spec=ColumnSpec(
            storage=S(type_=TZDateTime, nullable=False),
            field=F(py_type=dt.datetime),
            io=IO(in_verbs=("create",), out_verbs=("read", "list"), sortable=True),
        )
    )
    wildcard = acol(
        spec=ColumnSpec(
            storage=S(type_=Boolean, nullable=False, default=False),
            field=F(py_type=bool),
            io=IO(in_verbs=("create",), out_verbs=("read", "list")),
        )
    )
