from .AnthropicModel import AnthropicModel
from .AnthropicToolModel import AnthropicToolModel

__all__ = ["AnthropicModel", "AnthropicToolModel"]

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version("swarmauri_llm_anthropic")
except PackageNotFoundError:
    __version__ = "0.0.0"
