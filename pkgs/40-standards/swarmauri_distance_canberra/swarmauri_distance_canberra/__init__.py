from importlib.metadata import PackageNotFoundError, version
import warnings

from .CanberraDistance import CanberraDistance

warnings.warn(
    (
        "swarmauri_distance_canberra is deprecated and will be "
        "removed from the active workspace by v0.12.0."
    ),
    DeprecationWarning,
    stacklevel=2,
)

try:
    __version__ = version("swarmauri_distance_canberra")
except PackageNotFoundError:
    __version__ = "unknown"

__all__ = ["CanberraDistance", "__version__"]
