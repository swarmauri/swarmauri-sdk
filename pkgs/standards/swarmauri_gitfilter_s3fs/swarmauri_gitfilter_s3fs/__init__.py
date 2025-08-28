from .s3fs_filter import S3FSFilter

__all__ = ["S3FSFilter"]

try:  # pragma: no cover
    from importlib.metadata import version, PackageNotFoundError
except ImportError:  # pragma: no cover
    from importlib_metadata import version, PackageNotFoundError

try:  # pragma: no cover
    __version__ = version("swarmauri_gitfilter_s3fs")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"
