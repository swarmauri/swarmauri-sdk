from __future__ import annotations

from autoapi.v2.mixins import GUIDPk, UserMixin
from autoapi.v2.tables import Base

from .mixins import RepositoryMixin


class UserRepository(Base, GUIDPk, RepositoryMixin, UserMixin):
    """Edge capturing per-repository permissions for a user."""

    __tablename__ = "user_repositories"


__all__ = ["UserRepository"]
