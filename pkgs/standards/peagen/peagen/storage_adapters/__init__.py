from peagen.plugins.storage_adapters import (
    FileStorageAdapter,
    MinioStorageAdapter,
    GithubStorageAdapter,
    GithubReleaseStorageAdapter,
    make_adapter_for_uri,
)

__all__ = [
    "FileStorageAdapter",
    "MinioStorageAdapter",
    "GithubStorageAdapter",
    "GithubReleaseStorageAdapter",
    "make_adapter_for_uri",
]
