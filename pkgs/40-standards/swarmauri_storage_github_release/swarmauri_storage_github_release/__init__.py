from .gh_release_storage_adapter import GithubReleaseStorageAdapter

__all__ = ["GithubReleaseStorageAdapter"]

try:  # pragma: no cover
    from importlib.metadata import version, PackageNotFoundError
except ImportError:  # pragma: no cover
    from importlib_metadata import version, PackageNotFoundError

try:  # pragma: no cover
    __version__ = version("swarmauri_storage_github_release")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"
