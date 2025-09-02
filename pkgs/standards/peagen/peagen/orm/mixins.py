from __future__ import annotations

from autoapi.v3.types import (
    PgUUID,
    String,
    Mapped,
    declarative_mixin,
    declared_attr,
    relationship,
)
from autoapi.v3.specs import S, acol
from autoapi.v3.column.storage_spec import ForeignKeySpec


@declarative_mixin
class RepositoryMixin:
    """Mixin providing a required ``repository_id`` foreign key."""

    repository_id: Mapped[PgUUID] = acol(
        storage=S(
            PgUUID(as_uuid=True),
            fk=ForeignKeySpec("peagen.repositories.id"),
            nullable=False,
        )
    )


@declarative_mixin
class RepositoryRefMixin:
    """Mixin holding an optional reference to a repository and ref."""

    repository_id: Mapped[PgUUID | None] = acol(
        storage=S(
            PgUUID(as_uuid=True),
            fk=ForeignKeySpec("peagen.repositories.id", on_delete="CASCADE"),
            nullable=True,
        )
    )
    repo: Mapped[str] = acol(
        storage=S(String, nullable=False)
    )  # e.g. "github.com/acme/app"
    ref: Mapped[str] = acol(
        storage=S(String, nullable=False)
    )  # e.g. "main" / SHA / tag

    @declared_attr
    def repository(cls):
        return relationship(
            "Repository",
            back_populates="tasks",
            foreign_keys=lambda: [cls.repository_id],
        )


__all__ = ["RepositoryMixin", "RepositoryRefMixin"]
