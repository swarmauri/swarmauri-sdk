from importlib.metadata import PackageNotFoundError, version

from .exceptions import (
    WebDAVError,
    WebDAVInsufficientStorageError,
    WebDAVLockedError,
    WebDAVPreconditionError,
)
from .webdav_storage_adapter import WebDAVStorageAdapter

__all__ = [
    "WebDAVError",
    "WebDAVInsufficientStorageError",
    "WebDAVLockedError",
    "WebDAVPreconditionError",
    "WebDAVStorageAdapter",
]

try:
    __version__ = version("swarmauri_storage_webdav")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"
