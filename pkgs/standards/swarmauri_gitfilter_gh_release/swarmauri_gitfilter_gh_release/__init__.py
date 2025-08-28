from .gh_release_filter import GithubReleaseFilter

__all__ = ["GithubReleaseFilter"]

try:  # pragma: no cover
    from importlib.metadata import version, PackageNotFoundError
except ImportError:  # pragma: no cover
    from importlib_metadata import version, PackageNotFoundError

try:  # pragma: no cover
    __version__ = version("swarmauri_gitfilter_gh_release")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"
