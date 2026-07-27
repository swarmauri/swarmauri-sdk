from .GeminiProModel import GeminiProModel
from .GeminiToolModel import GeminiToolModel
from .GeminiVLM import GeminiVLM

__all__ = ["GeminiProModel", "GeminiToolModel", "GeminiVLM"]

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version("swarmauri_llm_gemini")
except PackageNotFoundError:
    __version__ = "0.0.0"
