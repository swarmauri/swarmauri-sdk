try:
    # For Python 3.8 and newer
    from importlib.metadata import version, PackageNotFoundError
except ImportError:  # pragma: no cover - fallback for older Python
    # For older Python versions, use the backport
    from importlib_metadata import version, PackageNotFoundError

try:
    __package_name__ = "peagen"
    __version__ = version(__package_name__)
except PackageNotFoundError:
    # If the package is not installed (for example, during development)
    __version__ = "0.0.0"


from .plugin_manager import PluginManager, resolve_plugin_spec
from .errors import (
    PatchTargetMissingError,
    SpecFileNotFoundError,
    TemplateFileNotFoundError,
    ProjectsPayloadValidationError,
    ProjectsPayloadFormatError,
    MissingProjectsListError,
)
from .core.patch_core import apply_patch

__all__ = [
    "__package_name__",
    "__version__",
    "PluginManager",
    "resolve_plugin_spec",
    "PatchTargetMissingError",
    "SpecFileNotFoundError",
    "TemplateFileNotFoundError",
    "ProjectsPayloadValidationError",
    "ProjectsPayloadFormatError",
    "MissingProjectsListError",
    "apply_patch",
]
