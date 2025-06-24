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


class SpecFileNotFoundError(FileNotFoundError):
    """Raised when the DOE specification file is missing."""

    def __init__(self, spec_path: str) -> None:
        super().__init__(spec_path)
        self.spec_path = spec_path

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"DOE spec file not found: {self.spec_path}"


class TemplateFileNotFoundError(FileNotFoundError):
    """Raised when the project template file is missing."""

    def __init__(self, template_path: str) -> None:
        super().__init__(template_path)
        self.template_path = template_path

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"Template file not found: {self.template_path}"


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

class InvalidPluginSpecError(ValueError):
    """Raised when a plugin reference cannot be parsed."""

    def __init__(self, spec: str) -> None:
        super().__init__(spec)
        self.spec = spec

    def __str__(self) -> str:  # pragma: no cover - trivial
        return (
            f"Invalid plugin specification '{self.spec}'. "
            "Expected 'module.Class' or 'module:Class'."
        )