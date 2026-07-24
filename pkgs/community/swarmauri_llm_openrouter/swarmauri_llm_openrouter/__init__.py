"""Expose OpenRouter implementations for Swarmauri model families."""

from importlib.metadata import PackageNotFoundError, version

from .OpenRouterImgGenModel import OpenRouterImgGenModel
from .OpenRouterModel import OpenRouterModel
from .OpenRouterToolModel import OpenRouterToolModel
from .OpenRouterVLM import OpenRouterVLM
from ._internal.catalog import OpenRouterModelCatalog
from ._internal.routing import OpenRouterProviderPreferences

__all__ = [
    "OpenRouterImgGenModel",
    "OpenRouterModel",
    "OpenRouterModelCatalog",
    "OpenRouterProviderPreferences",
    "OpenRouterToolModel",
    "OpenRouterVLM",
]

try:
    __version__ = version("swarmauri_llm_openrouter")
except PackageNotFoundError:
    __version__ = "0.0.0"
