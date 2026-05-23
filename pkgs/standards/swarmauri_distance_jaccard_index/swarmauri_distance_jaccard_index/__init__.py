from importlib.metadata import PackageNotFoundError, version
import warnings

from .JaccardIndexDistance import JaccardIndexDistance

warnings.warn(
    "swarmauri_distance_jaccard_index is deprecated and will be removed from the active workspace by v0.12.0.",
    DeprecationWarning,
    stacklevel=2,
)

try:
    __version__ = version("swarmauri_distance_jaccard_index")
except PackageNotFoundError:
    __version__ = "unknown"

__all__ = ["JaccardIndexDistance", "__version__"]
