"""
peagen/orm/__init__.py – aggregate of all Peagen domain tables.
"""

from __future__ import annotations

from typing import FrozenSet

from autoapi.v2.tables import Org, Role, RoleGrant, RolePerm, Status, Base

from .tenant import Tenant
from .user import User
from .repository import Repository
from .user_repository import UserRepository
from .raw_blob import RawBlob
from .keys import PublicKey, GPGKey, DeployKey
from .secrets import UserSecret, OrgSecret, RepoSecret
from .pools import Pool
from .workers import Worker
from .tasks import Action, SpecKind, Task
from .works import Work
from .mixins import RepositoryMixin, RepositoryRefMixin


def _is_terminal(cls, state: str | Status) -> bool:
    """Return True if *state* represents completion."""
    terminal: FrozenSet[str] = frozenset({"success", "failed", "cancelled", "rejected"})
    value = state.value if isinstance(state, Status) else state
    return value in terminal


Status.is_terminal = classmethod(_is_terminal)


__all__ = [
    "Tenant",
    "User",
    "Org",
    "Role",
    "RoleGrant",
    "RolePerm",
    "Status",
    "Base",
    "Repository",
    "RepositoryMixin",
    "RepositoryRefMixin",
    "UserRepository",
    "PublicKey",
    "GPGKey",
    "DeployKey",
    "UserSecret",
    "OrgSecret",
    "RepoSecret",
    "Pool",
    "Worker",
    "Action",
    "SpecKind",
    "Task",
    "Work",
    "RawBlob",
]
