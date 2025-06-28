"""Git filter implementations formerly known as storage adapters."""

from urllib.parse import urlparse

from .minio_filter import MinioFilter
from .gh_release_filter import GithubReleaseFilter
from .s3fs_filter import S3FSFilter
from .file_filter import FileFilter
from peagen.plugins import PluginManager
from peagen._utils.config_loader import resolve_cfg


def make_filter_for_uri(uri: str):
    """Return a git filter instance based on URI scheme."""
    scheme = urlparse(uri).scheme or "file"
    pm = PluginManager(resolve_cfg())
    try:
        cls = pm._resolve_spec("git_filters", scheme)
    except KeyError:
        raise ValueError(f"No git filter registered for scheme '{scheme}'")
    if not hasattr(cls, "from_uri"):
        raise TypeError(f"{cls.__name__} lacks required from_uri()")
    return cls.from_uri(uri)


__all__ = [
    "FileFilter",
    "MinioFilter",
    "GithubReleaseFilter",
    "S3FSFilter",
    "make_filter_for_uri",
]
