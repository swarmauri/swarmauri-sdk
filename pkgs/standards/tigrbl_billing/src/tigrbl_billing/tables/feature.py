"""Feature table – named entitlements and usage units."""

from __future__ import annotations

from enum import Enum
from tigrbl import Base
from tigrbl.orm.mixins import GUIDPk, Timestamped, ActiveToggle
from tigrbl.specs import F, IO, S, acol
from tigrbl.types import String, Text, JSONB, SAEnum, Mapped


class MeteringKind(str, Enum):
    NONE = "none"
    EVENT = "event"
    GAUGE = "gauge"


class Feature(Base, GUIDPk, Timestamped, ActiveToggle):
    __tablename__ = "billing_features"

    key: Mapped[str] = acol(
        storage=S(type_=String(100), unique=True, index=True, nullable=False),
        field=F(py_type=str, constraints={"max_length": 100}),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
    )

    name: Mapped[str] = acol(
        storage=S(type_=String(255), nullable=False, index=True),
        field=F(py_type=str, constraints={"max_length": 255}),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
    )

    description: Mapped[str | None] = acol(
        storage=S(type_=Text, nullable=True),
        field=F(py_type=str),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
    )

    metering: Mapped[MeteringKind] = acol(
        storage=S(
            type_=SAEnum(MeteringKind, name="feature_metering_kind"), nullable=False
        ),
        field=F(py_type=MeteringKind),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
    )

    unit_label: Mapped[str | None] = acol(
        storage=S(type_=String(32), nullable=True),
        field=F(py_type=str, constraints={"max_length": 32}),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
    )

    metadata: Mapped[dict | None] = acol(
        storage=S(type_=JSONB, nullable=True),
        field=F(py_type=dict),
        io=IO(in_verbs=("create", "update", "replace"), out_verbs=("read", "list")),
    )


__all__ = ["Feature", "MeteringKind"]
