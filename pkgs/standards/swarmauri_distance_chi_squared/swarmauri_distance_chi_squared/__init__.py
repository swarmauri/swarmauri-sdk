from importlib.metadata import PackageNotFoundError, version
import warnings

from .ChiSquaredDistance import ChiSquaredDistance

warnings.warn(
    (
        "swarmauri_distance_chi_squared is deprecated and will be "
        "removed from the active workspace by v0.12.0."
    ),
    DeprecationWarning,
    stacklevel=2,
)

try:
    __version__ = version("swarmauri_distance_chi_squared")
except PackageNotFoundError:
    __version__ = "unknown"

__all__ = ["ChiSquaredDistance", "__version__"]
