try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:  # pragma: no cover
    from importlib_metadata import PackageNotFoundError, version

from .s3fs_storage_adapter import S3FSStorageAdapter

__all__ = ["PackageNotFoundError", "S3FSStorageAdapter", "version"]
