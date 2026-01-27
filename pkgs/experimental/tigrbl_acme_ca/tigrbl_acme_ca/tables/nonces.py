from __future__ import annotations

import datetime as dt

from tigrbl.orm.tables import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.specs import acol, IO, F, S, ColumnSpec
from tigrbl.types import (
    String,
    Boolean,
    TZDateTime,
)


class Nonce(Base, GUIDPk):
    __tablename__ = "acme_nonces"
    __resource__ = "nonce"

    value = acol(
        spec=ColumnSpec(
            storage=S(type_=String(64), unique=True, index=True, nullable=False),
            field=F(py_type=str),
            io=IO(in_verbs=("create",), out_verbs=("read", "list")),
        )
    )
    used = acol(
        spec=ColumnSpec(
            storage=S(type_=Boolean, nullable=False, default=False),
            field=F(py_type=bool),
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
