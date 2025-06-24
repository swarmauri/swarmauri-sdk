"""peagen.exceptions

Exception classes used by the Peagen package.
"""


class PatchTargetMissingError(ValueError):
    """Patch operation refers to a non-existent path in the template."""


class WorkspaceNotFoundError(FileNotFoundError):
    """Raised when a workspace path cannot be materialised."""

    def __init__(self, workspace: str) -> None:
        super().__init__(workspace)
        self.workspace = workspace

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"Workspace '{self.workspace}' does not exist or is not accessible"


class GitOperationError(RuntimeError):
    """Raised when a git command fails."""

    pass


class GitRemoteMissingError(RuntimeError):
    """Raised when an expected git remote is not configured."""

    pass


class SchedulerError(RuntimeError):
    """Base class for errors raised during task scheduling."""


class MissingActionError(SchedulerError):
    """Raised when a task payload lacks the required 'action' key."""

    def __init__(self) -> None:
        super().__init__("Task payload missing 'action' key")


class NoWorkerAvailableError(SchedulerError):
    """Raised when no worker supports the requested action in the pool."""

    def __init__(self, pool: str, action: str) -> None:
        msg = f"No worker available in pool '{pool}' for action '{action}'"
        super().__init__(msg)
        self.pool = pool
        self.action = action
