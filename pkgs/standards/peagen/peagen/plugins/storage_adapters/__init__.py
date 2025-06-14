"""Factory helpers and built-in storage adapters."""

from urllib.parse import urlparse

from .file_storage_adapter import FileStorageAdapter
from .minio_storage_adapter import MinioStorageAdapter
from .github_storage_adapter import GithubStorageAdapter
from .gh_release_storage_adapter import GithubReleaseStorageAdapter
from .s3fs_storage_adapter import S3FSStorageAdapter
from peagen.plugins import registry


def make_adapter_for_uri(uri: str):
    """Return a storage adapter instance based on *uri* scheme."""
    scheme = urlparse(uri).scheme or "file"  # 'file' if path like /home/...
    try:
        adapter_cls = registry["storage_adapters"][scheme]
    except KeyError:
        raise ValueError(f"No storage adapter registered for scheme '{scheme}'")
    if not hasattr(adapter_cls, "from_uri"):
        raise TypeError(f"{adapter_cls.__name__} lacks required from_uri()")
    return adapter_cls.from_uri(uri)

__all__ = [
    "FileStorageAdapter",
    "MinioStorageAdapter",
    "GithubStorageAdapter",
    "GithubReleaseStorageAdapter",
    "S3FSStorageAdapter",
    "make_adapter_for_uri",
]
