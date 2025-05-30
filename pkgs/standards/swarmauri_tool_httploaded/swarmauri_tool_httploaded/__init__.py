from .HTTPLoadedTool import HTTPLoadedTool

__all__ = ["HTTPLoadedTool"]

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:  # pragma: no cover
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("swarmauri_tool_httploaded")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"
