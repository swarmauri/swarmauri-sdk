"""Service key model for the authentication service."""

from __future__ import annotations

from autoapi.v3.orm.tables import ApiKey as ApiKeyBase
from autoapi.v3.types import Mapped, PgUUID, UniqueConstraint, relationship
from autoapi.v3.specs import F, IO, S, acol
from autoapi.v3.column.storage_spec import ForeignKeySpec
from uuid import UUID
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    pass


class ServiceKey(ApiKeyBase):
    __tablename__ = "service_keys"
    __table_args__ = (
        UniqueConstraint("digest"),
        {"extend_existing": True, "schema": "authn"},
    )
    service_id: Mapped[UUID] = acol(
        storage=S(
            PgUUID(as_uuid=True),
            fk=ForeignKeySpec(target="authn.services.id"),
            index=True,
            nullable=False,
        ),
        field=F(py_type=UUID, required_in=("create",)),
        io=IO(in_verbs=("create",), out_verbs=("read", "list")),
    )

    _service = relationship(
        "Service",
        back_populates="_service_keys",
        lazy="joined",
    )


__all__ = ["ServiceKey"]
