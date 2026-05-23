from importlib.metadata import PackageNotFoundError, version
import warnings

from .LevenshteinDistance import LevenshteinDistance

warnings.warn(
    "swarmauri_distance_levenshtein is deprecated and will be removed from the active workspace by v0.12.0.",
    DeprecationWarning,
    stacklevel=2,
)

try:
    __version__ = version("swarmauri_distance_levenshtein")
except PackageNotFoundError:
    __version__ = "unknown"

__all__ = ["LevenshteinDistance", "__version__"]
