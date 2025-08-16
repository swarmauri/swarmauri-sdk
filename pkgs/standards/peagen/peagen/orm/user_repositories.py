from __future__ import annotations

from autoapi.v2.tables import Base
from autoapi.v2.mixins import GUIDPk, UserMixin

from .mixins import RepositoryMixin


class UserRepository(Base, GUIDPk, RepositoryMixin, UserMixin):
    """Edge capturing any per-repository permission or ownership the user may have."""

    __tablename__ = "user_repositories"
    __table_args__= ({"schema": "peagen"},)

__all__ = ["UserRepository"]
