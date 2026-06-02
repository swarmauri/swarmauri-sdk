try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:  # pragma: no cover
    from importlib_metadata import PackageNotFoundError, version

from .s3_storage_adapter import S3StorageAdapter

__all__ = ["PackageNotFoundError", "S3StorageAdapter", "version"]
