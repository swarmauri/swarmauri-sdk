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
    JSONB,
)


class AuditEvent(Base, GUIDPk):
    __tablename__ = "acme_audit_events"
    __resource__ = "audit_event"

    event_type = acol(
        spec=ColumnSpec(
            storage=S(type_=String(64), nullable=False, index=True),
            field=F(py_type=str),
            io=IO(in_verbs=("create",), out_verbs=("read", "list"), sortable=True),
        )
    )
    actor_account_id = acol(
        spec=ColumnSpec(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(target="acme_accounts.id"),
                nullable=True,
                index=True,
            ),
            field=F(py_type=UUIDType, allow_null_in=("create",)),
            io=IO(in_verbs=("create",), out_verbs=("read", "list")),
        )
    )
    object_type = acol(
        spec=ColumnSpec(
            storage=S(type_=String(64), nullable=True),
            field=F(py_type=str, allow_null_in=("create",)),
            io=IO(in_verbs=("create",), out_verbs=("read", "list")),
        )
    )
    object_id = acol(
        spec=ColumnSpec(
            storage=S(type_=String(128), nullable=True),
            field=F(py_type=str, allow_null_in=("create",)),
            io=IO(in_verbs=("create",), out_verbs=("read", "list")),
        )
    )
    payload = acol(
        spec=ColumnSpec(
            storage=S(type_=JSONB, nullable=True),
            field=F(py_type=dict, allow_null_in=("create",)),
            io=IO(in_verbs=("create",), out_verbs=("read", "list")),
        )
    )
    at = acol(
        spec=ColumnSpec(
            storage=S(
                type_=TZDateTime,
                nullable=False,
                default=lambda: dt.datetime.now(dt.timezone.utc),
            ),
            field=F(py_type=dt.datetime),
            io=IO(in_verbs=("create",), out_verbs=("read", "list"), sortable=True),
        )
    )
