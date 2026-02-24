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
    TZDateTime,
    JSONB,
    Text,
)


class Order(Base, GUIDPk, Timestamped):
    __tablename__ = "acme_orders"
    __resource__ = "order"

    account_id = acol(
        spec=ColumnSpec(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(target="acme_accounts.id"),
                nullable=False,
                index=True,
            ),
            field=F(py_type=UUIDType),
            io=IO(in_verbs=("create",), out_verbs=("read", "list")),
        )
    )
    status = acol(
        spec=ColumnSpec(
            storage=S(type_=String(24), nullable=False, default="pending"),
            field=F(
                py_type=str,
                examples=["pending", "ready", "processing", "valid", "invalid"],
            ),
            io=IO(out_verbs=("read", "list"), in_verbs=("update",), sortable=True),
        )
    )
    identifiers = acol(
        spec=ColumnSpec(
            storage=S(type_=JSONB, nullable=False, default=list),
            field=F(py_type=list),
            io=IO(in_verbs=("create",), out_verbs=("read", "list")),
        )
    )
    expires_at = acol(
        spec=ColumnSpec(
            storage=S(type_=TZDateTime, nullable=False),
            field=F(py_type=dt.datetime),
            io=IO(in_verbs=("create",), out_verbs=("read", "list"), sortable=True),
        )
    )
    csr_der_b64 = acol(
        spec=ColumnSpec(
            storage=S(type_=Text, nullable=True),
            field=F(py_type=str, allow_null_in=("update",)),
            io=IO(in_verbs=("update",), out_verbs=("read", "list")),
        )
    )
    certificate_id = acol(
        spec=ColumnSpec(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(target="acme_certificates.id"),
                nullable=True,
                index=True,
            ),
            field=F(py_type=UUIDType, allow_null_in=("update",)),
            io=IO(out_verbs=("read", "list"), in_verbs=("update",)),
        )
    )
