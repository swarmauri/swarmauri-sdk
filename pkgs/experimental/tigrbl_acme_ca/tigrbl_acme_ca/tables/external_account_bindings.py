from __future__ import annotations

import datetime as dt

from tigrbl.orm.tables import Base
from tigrbl.orm.mixins import GUIDPk, Timestamped
from tigrbl.specs import acol, IO, F, S, ColumnSpec
from tigrbl.types import (
    String,
    Boolean,
    TZDateTime,
)


class ExternalAccountBinding(Base, GUIDPk, Timestamped):
    __tablename__ = "acme_external_account_bindings"
    __resource__ = "external_account_binding"

    kid = acol(
        spec=ColumnSpec(
            storage=S(type_=String(120), unique=True, index=True, nullable=False),
            field=F(py_type=str),
            io=IO(in_verbs=("create",), out_verbs=("read", "list"), sortable=True),
        )
    )
    hmac_key_b64 = acol(
        spec=ColumnSpec(
            storage=S(type_=String(512), nullable=False),
            field=F(py_type=str),
            io=IO(in_verbs=("create",), out_verbs=("read", "list")),
        )
    )
    enabled = acol(
        spec=ColumnSpec(
            storage=S(type_=Boolean, nullable=False, default=True),
            field=F(py_type=bool),
            io=IO(in_verbs=("create", "update"), out_verbs=("read", "list")),
        )
    )
    expires_at = acol(
        spec=ColumnSpec(
            storage=S(type_=TZDateTime, nullable=True),
            field=F(py_type=dt.datetime, allow_null_in=("create", "update")),
            io=IO(
                in_verbs=("create", "update"), out_verbs=("read", "list"), sortable=True
            ),
        )
    )
