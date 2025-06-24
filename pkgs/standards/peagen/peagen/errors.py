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
