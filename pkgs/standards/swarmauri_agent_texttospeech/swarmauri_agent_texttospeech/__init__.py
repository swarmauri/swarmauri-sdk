from importlib.metadata import PackageNotFoundError, version

from .TextToSpeechAgent import TextToSpeechAgent

__all__ = ["TextToSpeechAgent"]

try:
    __version__ = version("swarmauri_agent_texttospeech")
except PackageNotFoundError:
    __version__ = "0.0.0"
