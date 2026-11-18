"""Expose the alpha openai text-to-speech component."""

from importlib.metadata import PackageNotFoundError, version

from .OpenaiTTS import OpenaiTTS

__all__ = ["OpenaiTTS"]

try:
    __version__ = version("swarmauri_tts_openai")
except PackageNotFoundError:
    __version__ = "0.0.0"
