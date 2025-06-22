from .JWTMiddleware import JWTMiddleware

__all__ = ["JWTMiddleware"]

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:  # pragma: no cover - for older Python versions
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version("swarmauri_middleware_jwt")
except PackageNotFoundError:  # pragma: no cover - package not installed
    __version__ = "0.0.0"
