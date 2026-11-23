from .WhisperLargeModel import WhisperLargeModel

__all__ = ["WhisperLargeModel"]

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version("swarmauri_llm_whisper")
except PackageNotFoundError:
    __version__ = "0.0.0"
