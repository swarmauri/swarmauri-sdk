from .UnionFactory import UnionFactory, UnionFactoryMetadata
from .IntersectionFactory import IntersectionFactory, IntersectionFactoryMetadata

__all__ = [
    "UnionFactory",
    "UnionFactoryMetadata",
    "IntersectionFactory",
    "IntersectionFactoryMetadata",
]

try:
    # For Python 3.8 and newer
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # For older Python versions, use the backport
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("swarmauri_typing")
except PackageNotFoundError:
    # If the package is not installed (for example, during development)
    __version__ = "0.0.0"
