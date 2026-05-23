from importlib.metadata import PackageNotFoundError, version
import warnings

from .SorensenDiceDistance import SorensenDiceDistance

warnings.warn(
    "swarmauri_distance_sorensen_dice is deprecated and will be removed from the active workspace by v0.12.0.",
    DeprecationWarning,
    stacklevel=2,
)

try:
    __version__ = version("swarmauri_distance_sorensen_dice")
except PackageNotFoundError:
    __version__ = "unknown"

__all__ = ["SorensenDiceDistance", "__version__"]
