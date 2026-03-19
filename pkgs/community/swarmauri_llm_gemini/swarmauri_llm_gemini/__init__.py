from .GeminiProModel import GeminiProModel
from .GeminiToolModel import GeminiToolModel

__all__ = ["GeminiProModel", "GeminiToolModel"]

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version("swarmauri_llm_gemini")
except PackageNotFoundError:
    __version__ = "0.0.0"
