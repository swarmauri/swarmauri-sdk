from importlib.metadata import PackageNotFoundError, version

from .XAIModel import XAIModel
from .XAIToolModel import XAIToolModel

try:
    __version__ = version("swarmauri_llm_xai")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = ["XAIModel", "XAIToolModel"]
