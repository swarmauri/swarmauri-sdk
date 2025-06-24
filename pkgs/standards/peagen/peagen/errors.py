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


class SpecFileNotFoundError(FileNotFoundError):
    """Raised when the DOE spec file is missing."""

    def __init__(self, path: str) -> None:
        super().__init__(path)
        self.path = path

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"DOE spec file not found: {self.path}"


class TemplateFileNotFoundError(FileNotFoundError):
    """Raised when the project template file is missing."""

    def __init__(self, path: str) -> None:
        super().__init__(path)
        self.path = path

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"Template file not found: {self.path}"
