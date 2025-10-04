from __future__ import annotations

import datetime as dt
from uuid import UUID

from tigrbl.orm.tables import Base
from tigrbl.orm.mixins import GUIDPk, Timestamped
from tigrbl.specs import acol, IO, F, S, ColumnSpec
from tigrbl.column.storage_spec import ForeignKeySpec
from tigrbl.types import (
    PgUUID, UUID as UUIDType, String, Boolean, TZDateTime, JSONB, Text, Integer,
    SAEnum, LargeBinary, Index
)

class Certificate(Base, GUIDPk, Timestamped):
    __tablename__ = "acme_certificates"
    __resource__ = "certificate"

    account_id = acol(
        spec=ColumnSpec(
            storage=S(type_=PgUUID(as_uuid=True), fk=ForeignKeySpec(target="acme_accounts.id"), nullable=False, index=True),
            field=F(py_type=UUIDType),
            io=IO(in_verbs=("create",), out_verbs=("read","list")),
        )
    )
    order_id = acol(
        spec=ColumnSpec(
            storage=S(type_=PgUUID(as_uuid=True), fk=ForeignKeySpec(target="acme_orders.id"), nullable=True, index=True),
            field=F(py_type=UUIDType, allow_null_in=("create","update")),
            io=IO(in_verbs=("create","update"), out_verbs=("read","list")),
        )
    )
    serial_hex = acol(
        spec=ColumnSpec(
            storage=S(type_=String(64), unique=True, index=True, nullable=False),
            field=F(py_type=str),
            io=IO(in_verbs=("create",), out_verbs=("read","list"), sortable=True),
        )
    )
    not_before = acol(
        spec=ColumnSpec(
            storage=S(type_=TZDateTime, nullable=False),
            field=F(py_type=dt.datetime),
            io=IO(in_verbs=("create",), out_verbs=("read","list")),
        )
    )
    not_after = acol(
        spec=ColumnSpec(
            storage=S(type_=TZDateTime, nullable=False),
            field=F(py_type=dt.datetime),
            io=IO(in_verbs=("create",), out_verbs=("read","list"), sortable=True),
        )
    )
    pem = acol(
        spec=ColumnSpec(
            storage=S(type_=Text, nullable=False),
            field=F(py_type=str),
            io=IO(out_verbs=("read","list")),  # write only through issuance op
        )
    )
