"""Expose the alpha deepgram TTS component."""

from importlib.metadata import PackageNotFoundError, version
from .DeepgramTTS import DeepgramTTS

__all__ = ["DeepgramTTS"]
try:
    __version__ = version("swarmauri_tts_deepgram")
except PackageNotFoundError:
    __version__ = "0.0.0"
