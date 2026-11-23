from importlib.metadata import PackageNotFoundError, version
import warnings

from .ManhattanDistance import ManhattanDistance

warnings.warn(
    (
        "swarmauri_distance_manhattan is deprecated and will be "
        "removed from the active workspace by v0.12.0."
    ),
    DeprecationWarning,
    stacklevel=2,
)

try:
    __version__ = version("swarmauri_distance_manhattan")
except PackageNotFoundError:
    __version__ = "unknown"

__all__ = ["ManhattanDistance", "__version__"]
