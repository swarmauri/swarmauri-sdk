from .FalAIVisionModel import FalAIVisionModel

__all__ = ["FalAIVisionModel"]

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version("swarmauri_llm_falai")
except PackageNotFoundError:
    __version__ = "0.0.0"
