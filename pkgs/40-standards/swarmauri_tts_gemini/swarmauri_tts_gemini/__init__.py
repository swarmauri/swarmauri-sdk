"""Expose the alpha gemini TTS component."""

from importlib.metadata import PackageNotFoundError, version
from .GeminiTTS import GeminiTTS

__all__ = ["GeminiTTS"]
try:
    __version__ = version("swarmauri_tts_gemini")
except PackageNotFoundError:
    __version__ = "0.0.0"
