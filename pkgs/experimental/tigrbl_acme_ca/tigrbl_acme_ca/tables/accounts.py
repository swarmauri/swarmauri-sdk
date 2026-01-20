from __future__ import annotations

import datetime as dt

from tigrbl.orm.tables import Base
from tigrbl.orm.mixins import GUIDPk, Timestamped
from tigrbl.specs import acol, IO, F, S, ColumnSpec
from tigrbl.types import (
    String,
    TZDateTime,
    JSONB,
)


class Account(Base, GUIDPk, Timestamped):
    __tablename__ = "acme_accounts"
    __resource__ = "account"

    key_thumbprint = acol(
        spec=ColumnSpec(
            storage=S(type_=String(128), nullable=False, index=True, unique=True),
            field=F(py_type=str, examples=["b64url-sha256-jwk-thumbprint"]),
            io=IO(in_verbs=("create",), out_verbs=("read", "list"), sortable=True),
        )
    )
    status = acol(
        spec=ColumnSpec(
            storage=S(type_=String(24), nullable=False, default="valid"),
            field=F(py_type=str, examples=["valid", "deactivated"]),
            io=IO(in_verbs=("update",), out_verbs=("read", "list"), sortable=True),
        )
    )
    contacts = acol(
        spec=ColumnSpec(
            storage=S(type_=JSONB, nullable=False, default=list),
            field=F(py_type=list),
            io=IO(in_verbs=("create", "update"), out_verbs=("read", "list")),
        )
    )
    external_binding = acol(
        spec=ColumnSpec(
            storage=S(type_=String(200), nullable=True),
            field=F(py_type=str, allow_null_in=("create", "update")),
            io=IO(in_verbs=("create", "update"), out_verbs=("read", "list")),
        )
    )
    deactivated_at = acol(
        spec=ColumnSpec(
            storage=S(type_=TZDateTime, nullable=True),
            field=F(py_type=dt.datetime, allow_null_in=("update",)),
            io=IO(out_verbs=("read", "list")),
        )
    )
