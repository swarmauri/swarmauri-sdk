"""Service key model for the authentication service."""

from __future__ import annotations

from uuid import UUID

from autoapi.v3.column.storage_spec import ForeignKeySpec
from autoapi.v3.orm.mixins import (
    Created,
    GUIDPk,
    KeyDigest,
    LastUsed,
    ValidityWindow,
)
from autoapi.v3.orm.tables._base import Base
from autoapi.v3.specs import F, IO, S, acol
from autoapi.v3.types import Mapped, PgUUID, String, relationship


class ServiceKey(Base, GUIDPk, Created, LastUsed, ValidityWindow, KeyDigest):
    __tablename__ = "service_keys"
    __table_args__ = {
        "extend_existing": True,
        "schema": "authn",
    }

    label: Mapped[str] = acol(
        storage=S(String, nullable=False),
        field=F(constraints={"max_length": 120}, required_in=("create",)),
        io=IO(in_verbs=("create",), out_verbs=("read", "list"), filter_ops=("eq",)),
    )

    service_id: Mapped[UUID] = acol(
        storage=S(
            PgUUID(as_uuid=True),
            fk=ForeignKeySpec(target="authn.services.id"),
            index=True,
            nullable=False,
        ),
        field=F(py_type=UUID, required_in=("create",)),
        io=IO(in_verbs=("create",), out_verbs=("read", "list"), filter_ops=("eq",)),
    )

    _service = relationship(
        "Service",
        back_populates="_service_keys",
        lazy="joined",
    )


__all__ = ["ServiceKey"]
