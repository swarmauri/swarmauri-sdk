from .TraceTimingMiddleware import TraceTimingMiddleware

__all__ = ["TraceTimingMiddleware"]

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:  # pragma: no cover
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version("swarmauri_middleware_tracetiming")
except PackageNotFoundError:
    __version__ = "0.0.0"
