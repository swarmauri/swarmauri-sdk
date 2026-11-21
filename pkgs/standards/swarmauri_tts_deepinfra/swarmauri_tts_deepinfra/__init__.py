"""Expose the alpha deepinfra text-to-speech component."""

from importlib.metadata import PackageNotFoundError, version

from .DeepInfraTTS import DeepInfraTTS

__all__ = ["DeepInfraTTS"]

try:
    __version__ = version("swarmauri_tts_deepinfra")
except PackageNotFoundError:
    __version__ = "0.0.0"
