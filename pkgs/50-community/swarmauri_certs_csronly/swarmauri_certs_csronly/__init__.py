from .CsrOnlyService import CsrOnlyService

__all__ = ["CsrOnlyService"]

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:  # pragma: no cover - Python <3.8
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("swarmauri_certs_csronly")
except PackageNotFoundError:  # pragma: no cover - package not installed
    __version__ = "0.0.0"
