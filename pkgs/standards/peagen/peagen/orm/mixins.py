from __future__ import annotations

from autoapi.v2.types import (
    Column,
    ForeignKey,
    PgUUID,
    String,
    declarative_mixin,
    declared_attr,
    foreign,
    relationship,
    remote,
)


@declarative_mixin
class RepositoryMixin:
    """Mixin providing a required ``repository_id`` foreign key."""

    repository_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("repositories.id"),
        nullable=False,
    )


@declarative_mixin
class RepositoryRefMixin:
    """Mixin holding an optional reference to a repository and ref."""

    repository_id = Column(
        PgUUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=True,
    )
    repo = Column(String, nullable=False)  # e.g. "github.com/acme/app"
    ref = Column(String, nullable=False)  # e.g. "main" / SHA / tag

    @declared_attr
    def repository(cls):
        from peagen.orm import Repository  # late import

        return relationship(
            "Repository",
            back_populates="tasks",
            primaryjoin=foreign(cls.repository_id) == remote(Repository.id),
        )


__all__ = ["RepositoryMixin", "RepositoryRefMixin"]
