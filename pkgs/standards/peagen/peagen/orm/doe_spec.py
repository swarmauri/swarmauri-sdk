from __future__ import annotations

from autoapi.v3.orm.tables import Base
from autoapi.v3.types import JSON, String, Text, UniqueConstraint, Mapped, relationship
from autoapi.v3.orm.mixins import GUIDPk, Timestamped, TenantBound, Ownable
from autoapi.v3.specs import S, acol
from typing import TYPE_CHECKING

from .users import User

if TYPE_CHECKING:  # pragma: no cover
    from .project_payload import ProjectPayload


class DoeSpec(Base, GUIDPk, Timestamped, TenantBound, Ownable):
    __tablename__ = "doe_specs"
    __table_args__ = (
        UniqueConstraint("tenant_id", "name"),
        {"schema": "peagen"},
    )

    name: Mapped[str] = acol(storage=S(String, nullable=False))
    schema_version: Mapped[str] = acol(
        storage=S(String, nullable=False, default="1.1.0")
    )
    description: Mapped[str | None] = acol(storage=S(Text, nullable=True))
    spec: Mapped[dict] = acol(storage=S(JSON, nullable=False))

    owner: Mapped[User] = relationship(User, lazy="selectin")
    project_payloads: Mapped[list["ProjectPayload"]] = relationship(
        "ProjectPayload",
        back_populates="doe_spec",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


__all__ = ["DoeSpec"]
