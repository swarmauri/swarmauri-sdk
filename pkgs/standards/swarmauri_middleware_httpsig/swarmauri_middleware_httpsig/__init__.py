from .HttpSigMiddleware import HttpSigMiddleware

__all__ = ["HttpSigMiddleware"]

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:  # pragma: no cover - fall back for older Python
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("swarmauri_middleware_httpsig")
except PackageNotFoundError:  # pragma: no cover - package not installed
    __version__ = "0.0.0"
