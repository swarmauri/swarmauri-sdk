from importlib.metadata import PackageNotFoundError, version
import warnings

from .CosineDistance import CosineDistance

warnings.warn(
    (
        "swarmauri_distance_cosine is deprecated and will be removed "
        "from the active workspace by v0.12.0."
    ),
    DeprecationWarning,
    stacklevel=2,
)

try:
    __version__ = version("swarmauri_distance_cosine")
except PackageNotFoundError:
    __version__ = "unknown"

__all__ = ["CosineDistance", "__version__"]
