from .PlayHTModel import PlayHTModel

__all__ = ["PlayHTModel"]

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version("swarmauri_llm_playht")
except PackageNotFoundError:
    __version__ = "0.0.0"
