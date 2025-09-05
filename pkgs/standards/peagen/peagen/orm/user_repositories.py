from __future__ import annotations

from autoapi.v3.orm.tables import Base
from autoapi.v3.orm.mixins import GUIDPk, UserColumn

from .mixins import RepositoryMixin


class UserRepository(Base, GUIDPk, RepositoryMixin, UserColumn):
    """Edge capturing any per-repository permission or ownership the user may have."""

    __tablename__ = "user_repositories"
    __table_args__ = ({"schema": "peagen"},)


__all__ = ["UserRepository"]
