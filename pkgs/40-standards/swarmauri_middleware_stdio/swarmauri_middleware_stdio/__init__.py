"""Expose middleware for logging HTTP requests and responses to stdout."""

from .StdioMiddleware import StdioMiddleware

__all__ = ["StdioMiddleware"]

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:  # pragma: no cover
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("swarmauri_middleware_stdio")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"
