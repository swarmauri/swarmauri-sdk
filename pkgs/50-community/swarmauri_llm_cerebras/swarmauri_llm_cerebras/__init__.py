from .CerebrasModel import CerebrasModel

__all__ = ["CerebrasModel"]

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version("swarmauri_llm_cerebras")
except PackageNotFoundError:
    __version__ = "0.0.0"
