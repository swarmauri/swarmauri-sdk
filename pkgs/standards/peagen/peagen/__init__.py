try:
    # For Python 3.8 and newer
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # For older Python versions, use the backport
    from importlib_metadata import version, PackageNotFoundError

try:
    __package_name__ = "peagen"
    __version__ = version(__package_name__)
except PackageNotFoundError:
    # If the package is not installed (for example, during development)
    __version__ = "0.0.0"


__all__ = ["__package_name__", "__version__"]