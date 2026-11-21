"""Authority records independent of credential format."""

from dataclasses import dataclass

from swarmauri_core.permissions import Permission


@dataclass(frozen=True)
class Grant:
    """Authorize a holder within a task and optional parent grant."""

    grant_id: str
    task_id: str
    subject: str
    holder: str
    tenant: str
    permissions: tuple[Permission, ...]
    expires_at: int
    remaining_depth: int
    parent_id: str | None = None
    revoked: bool = False
    revision: int = 0

    def __post_init__(self):
        if self.remaining_depth < 0:
            raise ValueError("Delegation depth must be non-negative")
        if not all((self.grant_id, self.task_id, self.subject, self.holder)):
            raise ValueError("Grant identity fields must be non-empty")
        if any(p.tenant != self.tenant for p in self.permissions):
            raise ValueError("Grant permissions must belong to its tenant")


@dataclass(frozen=True)
class DelegatedCredential:
    """Return a credential alongside its server-side authority record."""

    grant: Grant
    token: str


class GrantConflictError(RuntimeError):
    """Reject a duplicate grant or stale revision."""
