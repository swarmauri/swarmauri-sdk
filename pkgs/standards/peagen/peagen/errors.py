"""peagen.exceptions

Exception classes used by the Peagen package.
"""

from typing import Iterable


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


class TemplateSetInstallError(RuntimeError):
    """Raise when installing a template set distribution fails."""

    def __init__(self, name: str, reason: str) -> None:
        super().__init__(f"Failed to install template-set '{name}': {reason}")
        self.name = name
        self.reason = reason


class TemplateSetUninstallError(RuntimeError):
    """Raise when uninstalling a template set distribution fails."""

    def __init__(self, names: Iterable[str], reason: str) -> None:
        joined = ", ".join(names)
        super().__init__(f"Failed to uninstall template-set(s) [{joined}]: {reason}")
        self.names = list(names)
        self.reason = reason


class TemplateSearchPathError(RuntimeError):
    """Raise when no valid template directories can be found."""

    def __init__(self) -> None:
        super().__init__(
            "No valid template directories found — check plugin installation and .peagen.toml",
        )


class DependencySortError(RuntimeError):
    """Raise when dependency sorting of file records fails."""

    def __init__(self, reason: str) -> None:
        super().__init__(f"Dependency sort failed: {reason}")
        self.reason = reason


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


class GitCommitError(GitOperationError):
    """Raised when committing changes to the repository fails."""

    def __init__(self, paths: Iterable[str], reason: str | None = None) -> None:
        joined = ", ".join(paths)
        base = f"Failed to commit files [{joined}]. Ensure they exist inside the repository."
        msg = f"{base} Details: {reason}" if reason else base
        super().__init__(msg)
        self.paths = list(paths)
        self.reason = reason


class SchedulerError(RuntimeError):
    """Base class for errors raised during task scheduling."""


class MissingActionError(SchedulerError):
    """Raised when a task payload lacks the required 'action' key."""

    def __init__(self) -> None:
        super().__init__("Task payload missing 'action' key")


class MissingRepoError(SchedulerError):
    """Raised when a task payload lacks the required 'repo' key."""

    def __init__(self) -> None:
        super().__init__("Task payload missing 'repo' key")


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
            f"Invalid plugin specification '{self.spec}'. Expected an entry-point name."
        )


class PATNotAllowedError(RuntimeError):
    """Raised when a PAT token is passed to a forbidden command."""

    def __init__(self) -> None:
        super().__init__("PAT tokens are not allowed for this command")


class ProjectsPayloadValidationError(ValueError):
    """Raised when a projects_payload does not conform to the schema."""

    def __init__(self, errors: list[str], path: str | None = None) -> None:
        self.errors = errors
        self.path = path
        label = f" at '{path}'" if path else ""
        super().__init__(f"Invalid projects_payload{label}")

    def __str__(self) -> str:  # pragma: no cover - simple
        details = "; ".join(self.errors)
        loc = f" in {self.path}" if self.path else ""
        return f"Invalid projects_payload{loc}: {details}"


class TaskNotFoundError(RuntimeError):
    """Raised when a task id does not exist in the gateway."""

    def __init__(self, task_id: str) -> None:
        super().__init__(task_id)
        self.task_id = task_id

    def __str__(self) -> str:  # pragma: no cover - trivial
        return (
            f"Task '{self.task_id}' could not be found. "
            "It may have expired or was never created."
        )


class DispatchHTTPError(RuntimeError):
    """Raised when a worker responds with a non-200 HTTP status."""

    def __init__(self, status_code: int) -> None:
        super().__init__(f"Worker returned HTTP {status_code}")
        self.status_code = status_code


class MigrationFailureError(RuntimeError):
    """Raised when database migrations fail during startup."""

    def __init__(self, reason: str) -> None:
        super().__init__(f"Database migrations failed: {reason}")
        self.reason = reason


class HTTPClientNotInitializedError(RuntimeError):
    """Raised when an HTTP client is required but not yet initialized."""

    def __init__(self) -> None:
        super().__init__("HTTP client not initialized")


class ProjectsPayloadFormatError(ValueError):
    """Raised when a projects_payload is not a YAML mapping."""

    def __init__(self, found_type: str, path: str | None = None) -> None:
        self.found_type = found_type
        self.path = path
        loc = f" in {path}" if path else ""
        msg = f"projects_payload{loc} must be a YAML mapping, got {found_type}"
        super().__init__(msg)


class MissingProjectsListError(ValueError):
    """Raised when the projects_payload lacks a top-level PROJECTS list."""

    def __init__(self, path: str | None = None) -> None:
        self.path = path
        loc = f" in {path}" if path else ""
        super().__init__(f"projects_payload{loc} missing top-level 'PROJECTS' list")
