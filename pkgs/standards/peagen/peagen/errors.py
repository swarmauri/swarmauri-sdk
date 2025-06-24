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


class GitCloneError(GitOperationError):
    """Raised when cloning a repository fails."""

    def __init__(self, url: str) -> None:
        super().__init__(
            f"Failed to clone repository '{url}'. Ensure the URL is correct and accessible."
        )


class GitFetchError(GitOperationError):
    """Raised when fetching a ref from a remote fails."""

    def __init__(self, ref: str, remote: str) -> None:
        super().__init__(
            f"Failed to fetch '{ref}' from remote '{remote}'. Verify that the reference exists."
        )


class GitPushError(GitOperationError):
    """Raised when pushing changes to a remote fails."""

    def __init__(self, ref: str, remote: str) -> None:
        super().__init__(
            f"Failed to push '{ref}' to remote '{remote}'. Check remote configuration and permissions."
        )
