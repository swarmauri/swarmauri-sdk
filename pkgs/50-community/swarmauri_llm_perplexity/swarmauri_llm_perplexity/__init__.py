from .PerplexityModel import PerplexityModel

__all__ = ["PerplexityModel"]

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version("swarmauri_llm_perplexity")
except PackageNotFoundError:
    __version__ = "0.0.0"
