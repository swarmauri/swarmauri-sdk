from .file_filter import FileFilter

__all__ = ["FileFilter"]

try:  # pragma: no cover
    from importlib.metadata import version, PackageNotFoundError
except ImportError:  # pragma: no cover
    from importlib_metadata import version, PackageNotFoundError

try:  # pragma: no cover
    __version__ = version("swarmauri_gitfilter_file")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"
