from __future__ import annotations

from autoapi.v3.orm.tables import Base
from autoapi.v3.types import (
    JSON,
    String,
    Text,
    UniqueConstraint,
    PgUUID,
    Mapped,
    relationship,
)
from autoapi.v3.orm.mixins import GUIDPk, Timestamped, TenantBound, Ownable
from autoapi.v3.specs import S, acol
from autoapi.v3.column.storage_spec import ForeignKeySpec
from typing import TYPE_CHECKING

from .users import User

if TYPE_CHECKING:  # pragma: no cover
    from .doe_spec import DoeSpec


class ProjectPayload(Base, GUIDPk, Timestamped, TenantBound, Ownable):
    __tablename__ = "project_payloads"

    __table_args__ = (
        UniqueConstraint("tenant_id", "name"),
        {"schema": "peagen"},
    )

    doe_spec_id: Mapped[PgUUID | None] = acol(
        storage=S(
            PgUUID(as_uuid=True),
            fk=ForeignKeySpec("peagen.doe_specs.id", on_delete="SET NULL"),
            nullable=True,
        )
    )
    name: Mapped[str] = acol(storage=S(String, nullable=False))
    schema_version: Mapped[str] = acol(
        storage=S(String, nullable=False, default="1.0.0")
    )
    description: Mapped[str | None] = acol(storage=S(Text, nullable=True))
    payload: Mapped[dict] = acol(storage=S(JSON, nullable=False))

    owner: Mapped[User] = relationship(User, lazy="selectin")
    doe_spec: Mapped["DoeSpec | None"] = relationship(
        "DoeSpec", back_populates="project_payloads", lazy="selectin"
    )


__all__ = ["ProjectPayload"]
