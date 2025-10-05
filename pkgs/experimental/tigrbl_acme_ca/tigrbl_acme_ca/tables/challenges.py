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

class Challenge(Base, GUIDPk, Timestamped):
    __tablename__ = "acme_challenges"
    __resource__ = "challenge"

    authorization_id = acol(
        spec=ColumnSpec(
            storage=S(type_=PgUUID(as_uuid=True), fk=ForeignKeySpec(target="acme_authorizations.id"), nullable=False, index=True),
            field=F(py_type=UUIDType),
            io=IO(in_verbs=("create",), out_verbs=("read","list")),
        )
    )
    type = acol(
        spec=ColumnSpec(
            storage=S(type_=String(24), nullable=False),
            field=F(py_type=str, examples=["http-01","dns-01","tls-alpn-01"]),
            io=IO(in_verbs=("create",), out_verbs=("read","list"), sortable=True),
        )
    )
    status = acol(
        spec=ColumnSpec(
            storage=S(type_=String(24), nullable=False, default="pending"),
            field=F(py_type=str, examples=["pending","processing","valid","invalid"]),
            io=IO(in_verbs=("update",), out_verbs=("read","list"), sortable=True),
        )
    )
    token = acol(
        spec=ColumnSpec(
            storage=S(type_=String(255), nullable=True, index=True),
            field=F(py_type=str, allow_null_in=("create","update")),
            io=IO(in_verbs=("create","update"), out_verbs=("read","list")),
        )
    )
    validated_at = acol(
        spec=ColumnSpec(
            storage=S(type_=TZDateTime, nullable=True),
            field=F(py_type=dt.datetime, allow_null_in=("update",)),
            io=IO(in_verbs=("update",), out_verbs=("read","list")),
        )
    )
