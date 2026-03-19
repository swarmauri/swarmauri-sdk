from .LlamaCppModel import LlamaCppModel

__all__ = ["LlamaCppModel"]

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version("swarmauri_llm_llamacpp")
except PackageNotFoundError:
    __version__ = "0.0.0"
