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


class GitFetchError(GitOperationError):
    """Raised when fetching from a remote fails."""

    def __init__(self, remote: str, ref: str, url: str, reason: str) -> None:
        super().__init__(
            f"Failed to fetch '{ref}' from remote '{remote}' ({url}): {reason}"
        )
        self.remote = remote
        self.ref = ref
        self.url = url
        self.reason = reason


class GitPushError(GitOperationError):
    """Raised when pushing to a remote fails."""

    def __init__(self, remote: str, ref: str, url: str, reason: str) -> None:
        super().__init__(
            f"Failed to push '{ref}' to remote '{remote}' ({url}): {reason}"
        )
        self.remote = remote
        self.ref = ref
        self.url = url
        self.reason = reason
