from importlib.metadata import PackageNotFoundError, version

from .CloudflareWorkersAIModel import CloudflareWorkersAIModel
from .CloudflareWorkersAIToolModel import CloudflareWorkersAIToolModel

try:
    __version__ = version("swarmauri_llm_cloudflare")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = ["CloudflareWorkersAIModel", "CloudflareWorkersAIToolModel"]
