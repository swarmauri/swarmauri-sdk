from importlib.metadata import PackageNotFoundError, version

from .AzureOpenAIChatRetryPolicy import AzureOpenAIChatRetryPolicy
from .AzureOpenAIModel import AzureOpenAIModel
from .AzureOpenAIToolModel import AzureOpenAIToolModel

try:
    __version__ = version("swarmauri_llm_azureopenai")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = [
    "AzureOpenAIChatRetryPolicy",
    "AzureOpenAIModel",
    "AzureOpenAIToolModel",
]
