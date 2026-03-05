from __future__ import annotations

import datetime as dt
from decimal import Decimal

from ...specs import ColumnSpec, F, IO, S, acol
from ...types import (
    TZDateTime,
    PgUUID,
    String,
    SAEnum,
    Numeric,
    JSONB,
    TSVECTOR,
    UUID,
    Index,
    declarative_mixin,
    declared_attr,
    Mapped,
)

from .utils import tzutcnow, tzutcnow_plus_day, CRUD_IO


@declarative_mixin
class Slugged:
    slug: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(type_=String, unique=True, nullable=False),
            field=F(py_type=str, constraints={"max_length": 120}),
            io=CRUD_IO,
        )
    )


@declarative_mixin
class StatusColumn:
    status: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(
                type_=SAEnum(
                    "queued",
                    "waiting",
                    "input_required",
                    "auth_required",
                    "approved",
                    "rejected",
                    "dispatched",
                    "running",
                    "paused",
                    "success",
                    "failed",
                    "cancelled",
                    name="status_enum",
                ),
                default="waiting",
                nullable=False,
            ),
            field=F(py_type=str),
            io=CRUD_IO,
        )
    )


@declarative_mixin
class ValidityWindow:
    valid_from: Mapped[dt.datetime] = acol(
        spec=ColumnSpec(
            storage=S(type_=TZDateTime, default=tzutcnow, nullable=False),
            field=F(py_type=dt.datetime),
            io=CRUD_IO,
        )
    )
    valid_to: Mapped[dt.datetime | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=TZDateTime, default=tzutcnow_plus_day),
            field=F(py_type=dt.datetime),
            io=CRUD_IO,
        )
    )


@declarative_mixin
class Monetary:
    amount: Mapped[Decimal] = acol(
        spec=ColumnSpec(
            storage=S(type_=Numeric(18, 2), nullable=False),
            field=F(py_type=Decimal),
            io=CRUD_IO,
        )
    )
    currency: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(type_=String, default="USD", nullable=False),
            field=F(py_type=str, constraints={"max_length": 3}),
            io=CRUD_IO,
        )
    )


@declarative_mixin
class ExtRef:
    external_id: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(type_=String),
            field=F(py_type=str),
            io=CRUD_IO,
        )
    )
    provider: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(type_=String),
            field=F(py_type=str),
            io=CRUD_IO,
        )
    )


@declarative_mixin
class MetaJSON:
    meta: Mapped[dict] = acol(
        spec=ColumnSpec(
            storage=S(type_=JSONB, default=dict),
            field=F(py_type=dict),
            io=CRUD_IO,
        )
    )


@declarative_mixin
class BlobRef:
    blob_id: Mapped[UUID | None] = acol(
        spec=ColumnSpec(
            storage=S(type_=PgUUID(as_uuid=True)),
            field=F(py_type=UUID),
            io=CRUD_IO,
        )
    )


@declarative_mixin
class SearchVector:
    tsv: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(type_=TSVECTOR),
            field=F(py_type=str),
            io=IO(),
        )
    )

    @declared_attr
    def __table_args__(cls):
        return (Index(f"ix_{cls.__tablename__}_tsv", "tsv"),)


__all__ = [
    "Slugged",
    "StatusColumn",
    "ValidityWindow",
    "Monetary",
    "ExtRef",
    "MetaJSON",
    "BlobRef",
    "SearchVector",
]
