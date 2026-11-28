import warnings

from importlib.metadata import PackageNotFoundError, version

from .PlayHTModel import PlayHTModel

__all__ = ["PlayHTModel"]

try:
    __version__ = version("swarmauri_tts_playht")
except PackageNotFoundError:
    __version__ = "0.0.0"

# FutureWarning is visible to applications with Python default filters.
warnings.warn(
    "swarmauri_tts_playht is deprecated: Play.ht is discontinued. "
    "Use swarmauri_tts_openai.OpenaiTTS or another TTS provider.",
    FutureWarning,
    stacklevel=2,
)
