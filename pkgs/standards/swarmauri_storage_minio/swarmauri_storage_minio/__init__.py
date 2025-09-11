from .minio_storage_adapter import MinioStorageAdapter

__all__ = ["MinioStorageAdapter"]

try:  # pragma: no cover
    from importlib.metadata import version, PackageNotFoundError
except ImportError:  # pragma: no cover
    from importlib_metadata import version, PackageNotFoundError

try:  # pragma: no cover
    __version__ = version("swarmauri_storage_minio")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"
