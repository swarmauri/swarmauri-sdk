"""Expose the alpha cartesia TTS component."""

from importlib.metadata import PackageNotFoundError, version
from .CartesiaTTS import CartesiaTTS

__all__ = ["CartesiaTTS"]
try:
    __version__ = version("swarmauri_tts_cartesia")
except PackageNotFoundError:
    __version__ = "0.0.0"
