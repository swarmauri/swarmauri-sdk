"""Expose the alpha elevenlabs TTS component."""

from importlib.metadata import PackageNotFoundError, version
from .ElevenLabsTTS import ElevenLabsTTS

__all__ = ["ElevenLabsTTS"]
try:
    __version__ = version("swarmauri_tts_elevenlabs")
except PackageNotFoundError:
    __version__ = "0.0.0"
