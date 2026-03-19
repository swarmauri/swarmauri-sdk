from .OpenAIAudio import OpenAIAudio
from .OpenAIAudioTTS import OpenAIAudioTTS
from .OpenAIModel import OpenAIModel
from .OpenAIReasonModel import OpenAIReasonModel
from .OpenAIToolModel import OpenAIToolModel

__all__ = [
    "OpenAIAudio",
    "OpenAIAudioTTS",
    "OpenAIModel",
    "OpenAIReasonModel",
    "OpenAIToolModel",
]

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version("swarmauri_llm_openai")
except PackageNotFoundError:
    __version__ = "0.0.0"
