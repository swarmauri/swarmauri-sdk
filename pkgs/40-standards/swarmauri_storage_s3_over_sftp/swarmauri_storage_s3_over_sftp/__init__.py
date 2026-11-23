try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:  # pragma: no cover
    from importlib_metadata import PackageNotFoundError, version

from .s3_over_sftp_storage_adapter import S3OverSftpStorageAdapter

__all__ = ["PackageNotFoundError", "S3OverSftpStorageAdapter", "version"]
