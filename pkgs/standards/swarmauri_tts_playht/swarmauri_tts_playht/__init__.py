from importlib.metadata import PackageNotFoundError, version

from .PlayHTModel import PlayHTModel

__all__ = ["PlayHTModel"]

try:
    __version__ = version("swarmauri_tts_playht")
except PackageNotFoundError:
    __version__ = "0.0.0"
