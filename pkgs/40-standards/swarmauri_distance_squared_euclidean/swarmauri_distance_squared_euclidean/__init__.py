from importlib.metadata import PackageNotFoundError, version
import warnings

from .SquaredEuclideanDistance import SquaredEuclideanDistance

warnings.warn(
    (
        "swarmauri_distance_squared_euclidean is deprecated and will "
        "be removed from the active workspace by v0.12.0."
    ),
    DeprecationWarning,
    stacklevel=2,
)

try:
    __version__ = version("swarmauri_distance_squared_euclidean")
except PackageNotFoundError:
    __version__ = "unknown"

__all__ = ["SquaredEuclideanDistance", "__version__"]
