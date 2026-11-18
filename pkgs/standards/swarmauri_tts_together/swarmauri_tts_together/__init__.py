"""Expose the alpha together text-to-speech component."""

from importlib.metadata import PackageNotFoundError, version

from .TogetherTTS import TogetherTTS

__all__ = ["TogetherTTS"]

try:
    __version__ = version("swarmauri_tts_together")
except PackageNotFoundError:
    __version__ = "0.0.0"
