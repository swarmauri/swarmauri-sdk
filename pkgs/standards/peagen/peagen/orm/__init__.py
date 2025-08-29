"""
peagen.orm – aggregate and expose ORM table classes.
"""

from __future__ import annotations

from typing import FrozenSet

# from autoapi.v3.tables import Role, RoleGrant, RolePerm
from autoapi.v3.tables import Status, Base

# Import table classes. Ensure Tenant is imported before Pool so bootstrapping
# default rows inserts the default tenant prior to default pools.
from .tenants import Tenant
from .users import User
from .orgs import Org
from .repositories import Repository
from .user_repositories import UserRepository
from .raw_blobs import RawBlob
from .keys import PublicKey, GPGKey, DeployKey
from .secrets import UserSecret, OrgSecret, RepoSecret
from .tasks import Action, SpecKind, Task
from .works import Work
from .doe_spec import DoeSpec
from .evolve_spec import EvolveSpec
from .project_payload import ProjectPayload
from .peagen_toml_spec import PeagenTomlSpec
from .eval_result import EvalResult
from .analysis_result import AnalysisResult
from .pools import Pool
from .workers import Worker
from .mixins import RepositoryMixin, RepositoryRefMixin


def _is_terminal(cls, state: str | Status) -> bool:
    """Return True if *state* represents completion."""
    terminal: FrozenSet[str] = frozenset({"success", "failed", "cancelled", "rejected"})
    value = state.value if isinstance(state, Status) else state
    return value in terminal


Status.is_terminal = classmethod(_is_terminal)

# Convenience aliases for lowercase access
for _member in Status:
    setattr(Status, _member.value, _member)

# Legacy alias used by CLI for retries
setattr(Status, "retry", Status.queued)

__all__ = [
    "Tenant",
    "User",
    "Org",
    # "Role",
    # "RoleGrant",
    # "RolePerm",
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
    "DoeSpec",
    "EvolveSpec",
    "ProjectPayload",
    "PeagenTomlSpec",
    "EvalResult",
    "AnalysisResult",
]
