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
