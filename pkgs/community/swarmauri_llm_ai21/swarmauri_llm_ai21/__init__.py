from .AI21StudioModel import AI21StudioModel

__all__ = ["AI21StudioModel"]

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version("swarmauri_llm_ai21")
except PackageNotFoundError:
    __version__ = "0.0.0"
