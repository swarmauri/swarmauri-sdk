"""Expose OpenRouter implementations for Swarmauri model families."""

from importlib.metadata import PackageNotFoundError, version

from swarmauri_provider_openrouter import (
    OpenRouterModelCatalog,
    OpenRouterProvider,
    OpenRouterProviderPreferences,
)

from .OpenRouterImgGenModel import OpenRouterImgGenModel
from .OpenRouterModel import OpenRouterModel
from .OpenRouterRetryPolicy import OpenRouterRetryPolicy
from .OpenRouterToolModel import OpenRouterToolModel
from .OpenRouterVLM import OpenRouterVLM

__all__ = [
    "OpenRouterImgGenModel",
    "OpenRouterModel",
    "OpenRouterModelCatalog",
    "OpenRouterProvider",
    "OpenRouterProviderPreferences",
    "OpenRouterRetryPolicy",
    "OpenRouterToolModel",
    "OpenRouterVLM",
]

try:
    __version__ = version("swarmauri_llm_openrouter")
except PackageNotFoundError:
    __version__ = "0.0.0"
