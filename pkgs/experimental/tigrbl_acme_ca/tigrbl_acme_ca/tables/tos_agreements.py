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

class TosAgreement(Base, GUIDPk):
    __tablename__ = "acme_tos_agreements"
    __resource__ = "tos_agreement"

    account_id = acol(
        spec=ColumnSpec(
            storage=S(type_=PgUUID(as_uuid=True), fk=ForeignKeySpec(target="acme_accounts.id"), nullable=False, index=True),
            field=F(py_type=UUIDType),
            io=IO(in_verbs=("create",), out_verbs=("read","list")),
        )
    )
    agreed = acol(
        spec=ColumnSpec(
            storage=S(type_=Boolean, nullable=False, default=True),
            field=F(py_type=bool),
            io=IO(in_verbs=("create",), out_verbs=("read","list")),
        )
    )
    at = acol(
        spec=ColumnSpec(
            storage=S(type_=TZDateTime, nullable=False, default=lambda: dt.datetime.now(dt.timezone.utc)),
            field=F(py_type=dt.datetime),
            io=IO(in_verbs=("create",), out_verbs=("read","list")),
        )
    )
