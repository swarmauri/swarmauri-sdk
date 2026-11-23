"""Versioned business tasks, separate from execution checkpoints."""

from dataclasses import dataclass

from swarmauri_core.permissions import Permission


@dataclass(frozen=True)
class TaskRecord:
    """Persist the admitted authority and lifecycle intent for one task."""

    task_id: str
    subject: str
    tenant: str
    permissions: tuple[Permission, ...]
    expires_at: int
    status: str = "active"
    revision: int = 0
    execution_ids: tuple[str, ...] = ()

    def __post_init__(self):
        if self.status not in {"active", "paused", "stopped"}:
            raise ValueError("Invalid task status")
        if not self.task_id or not self.subject or not self.tenant:
            raise ValueError("Task identity fields must be non-empty")
        if any(p.tenant != self.tenant for p in self.permissions):
            raise ValueError("Task permissions must belong to its tenant")


class TaskConflictError(RuntimeError):
    """Reject an insert conflict or stale task revision."""
