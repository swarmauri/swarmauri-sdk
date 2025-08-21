from .IntrospectionTokenService import IntrospectionTokenService

__all__ = ["IntrospectionTokenService"]

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:  # pragma: no cover
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version("swarmauri_token_introspection")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"
