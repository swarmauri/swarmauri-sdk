"""Git filter implementations formerly known as storage adapters."""

from urllib.parse import urlparse

from .minio_filter import MinioFilter
from .gh_release_filter import GithubReleaseFilter
from .s3fs_filter import S3FSFilter
from peagen.plugins import registry


def make_filter_for_uri(uri: str):
    """Return a git filter instance based on URI scheme."""
    scheme = urlparse(uri).scheme or "file"
    try:
        cls = registry["git_filters"][scheme]
    except KeyError:
        raise ValueError(f"No git filter registered for scheme '{scheme}'")
    if not hasattr(cls, "from_uri"):
        raise TypeError(f"{cls.__name__} lacks required from_uri()")
    return cls.from_uri(uri)

__all__ = [
    "MinioFilter",
    "GithubReleaseFilter",
    "S3FSFilter",
    "make_filter_for_uri",
]
