from .file_storage_adapter import FileStorageAdapter

__all__ = ["FileStorageAdapter"]

try:  # pragma: no cover
    from importlib.metadata import version, PackageNotFoundError
except ImportError:  # pragma: no cover
    from importlib_metadata import version, PackageNotFoundError

try:  # pragma: no cover
    __version__ = version("swarmauri_storage_file")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"
